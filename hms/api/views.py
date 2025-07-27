from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import CustomUser
from rooms.models import Room, RoomType, Amenity
from bookings.models import Booking
from guests.models import Guest

from .serializers import (
    CustomUserSerializer, LoginSerializer, RoomSerializer, RoomTypeSerializer,
    AmenitySerializer, BookingSerializer, BookingListSerializer, GuestSerializer,
    DashboardStatsSerializer
)


# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="ثبت نام کاربر",
        operation_description="ایجاد حساب کاربری جدید در سیستم مدیریت هتل",
        responses={201: CustomUserSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': CustomUserSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="ورود کاربر",
        operation_description="احراز هویت کاربر و دریافت توکن دسترسی",
        request_body=LoginSerializer,
        responses={200: openapi.Response(
            description="ورود موفقیت‌آمیز",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        
        return Response({
            'user': CustomUserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="خروج کاربر",
        operation_description="خروج کاربر از سیستم و باطل کردن توکن",
        responses={200: openapi.Response(
            description="خروج موفقیت‌آمیز",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )}
    )
    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass
        
        logout(request)
        return Response({'message': 'Logout successful'})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="مشاهده پروفایل",
        operation_description="دریافت اطلاعات پروفایل کاربر فعلی"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش پروفایل",
        operation_description="به‌روزرسانی اطلاعات پروفایل کاربر فعلی"
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش بخشی از پروفایل",
        operation_description="به‌روزرسانی بخشی از اطلاعات پروفایل کاربر فعلی"
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


# Dashboard Views
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="آمار داشبورد",
        operation_description="دریافت آمار و اطلاعات کلی برای داشبورد مدیریتی",
        responses={200: DashboardStatsSerializer}
    )
    def get(self, request):
        today = timezone.now().date()
        current_month = timezone.now().replace(day=1).date()
        
        # Room statistics
        room_stats = Room.objects.aggregate(
            total=Count('id'),
            available=Count('id', filter=Q(status='available')),
            occupied=Count('id', filter=Q(status='occupied')),
            reserved=Count('id', filter=Q(status='reserved')),
            maintenance=Count('id', filter=Q(status='maintenance'))
        )
        
        # Booking statistics
        booking_stats = Booking.objects.aggregate(
            total=Count('id'),
            todays_checkins=Count('id', filter=Q(check_in=today)),
            todays_checkouts=Count('id', filter=Q(check_out=today))
        )
        
        # Calculate occupancy rate
        occupancy_rate = 0
        if room_stats['total'] > 0:
            occupied_and_reserved = room_stats['occupied'] + room_stats['reserved']
            occupancy_rate = (occupied_and_reserved / room_stats['total']) * 100
        
        # Revenue calculations (simplified)
        revenue_today = Booking.objects.filter(
            check_in=today,
            status__in=['checked_in', 'checked_out']
        ).aggregate(
            total=Sum('room__price')
        )['total'] or 0
        
        revenue_month = Booking.objects.filter(
            check_in__gte=current_month,
            status__in=['checked_in', 'checked_out']
        ).aggregate(
            total=Sum('room__price')
        )['total'] or 0
        
        stats_data = {
            **room_stats,
            **booking_stats,
            'occupancy_rate': round(occupancy_rate, 2),
            'revenue_today': revenue_today,
            'revenue_month': revenue_month
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data)


# Room Management Views
class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all().select_related('room_type').prefetch_related('amenities')
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'number'

    @swagger_auto_schema(
        operation_summary="فهرست اتاق‌ها",
        operation_description="دریافت لیست تمام اتاق‌های هتل",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="فیلتر بر اساس وضعیت اتاق", type=openapi.TYPE_STRING),
            openapi.Parameter('room_type', openapi.IN_QUERY, description="فیلتر بر اساس نوع اتاق", type=openapi.TYPE_INTEGER),
            openapi.Parameter('floor', openapi.IN_QUERY, description="فیلتر بر اساس طبقه", type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="جزئیات اتاق",
        operation_description="دریافت جزئیات کامل یک اتاق خاص"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ایجاد اتاق",
        operation_description="ایجاد اتاق جدید در سیستم"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش اتاق",
        operation_description="به‌روزرسانی اطلاعات یک اتاق"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش بخشی از اتاق",
        operation_description="به‌روزرسانی بخشی از اطلاعات یک اتاق"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="حذف اتاق",
        operation_description="حذف یک اتاق از سیستم"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by room type
        room_type = self.request.query_params.get('room_type')
        if room_type:
            queryset = queryset.filter(room_type_id=room_type)
        
        # Filter by floor
        floor = self.request.query_params.get('floor')
        if floor:
            queryset = queryset.filter(floor=floor)
        
        return queryset


class RoomTypeViewSet(ModelViewSet):
    queryset = RoomType.objects.all().prefetch_related('default_amenities')
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="فهرست انواع اتاق",
        operation_description="دریافت لیست تمام انواع اتاق‌های هتل"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="جزئیات نوع اتاق",
        operation_description="دریافت جزئیات کامل یک نوع اتاق خاص"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ایجاد نوع اتاق",
        operation_description="ایجاد نوع اتاق جدید در سیستم"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش نوع اتاق",
        operation_description="به‌روزرسانی اطلاعات یک نوع اتاق"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش بخشی از نوع اتاق",
        operation_description="به‌روزرسانی بخشی از اطلاعات یک نوع اتاق"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="حذف نوع اتاق",
        operation_description="حذف یک نوع اتاق از سیستم"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AmenityViewSet(ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="فهرست امکانات",
        operation_description="دریافت لیست تمام امکانات قابل ارائه در اتاق‌های هتل"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="جزئیات امکان",
        operation_description="دریافت جزئیات کامل یک امکان خاص"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ایجاد امکان",
        operation_description="ایجاد امکان جدید در سیستم"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش امکان",
        operation_description="به‌روزرسانی اطلاعات یک امکان"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش بخشی از امکان",
        operation_description="به‌روزرسانی بخشی از اطلاعات یک امکان"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="حذف امکان",
        operation_description="حذف یک امکان از سیستم"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all().select_related('room', 'primary_guest', 'assigned_staff')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer

    @swagger_auto_schema(
        operation_summary="فهرست رزروها",
        operation_description="دریافت لیست تمام رزروهای هتل",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="فیلتر بر اساس وضعیت رزرو", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="فیلتر رزروها از تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="فیلتر رزروها تا تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('show_trash', openapi.IN_QUERY, description="نمایش رزروهای حذف شده", type=openapi.TYPE_BOOLEAN),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="جزئیات رزرو",
        operation_description="دریافت جزئیات کامل یک رزرو خاص"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ایجاد رزرو",
        operation_description="ایجاد رزرو جدید در سیستم"
    )
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to create booking',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="ویرایش رزرو",
        operation_description="به‌روزرسانی اطلاعات یک رزرو"
    )
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to update booking',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="ویرایش بخشی از رزرو",
        operation_description="به‌روزرسانی بخشی از اطلاعات یک رزرو"
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to update booking',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="حذف رزرو",
        operation_description="حذف یک رزرو از سیستم"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_trash=False)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(check_in__gte=start_date)
        if end_date:
            queryset = queryset.filter(check_out__lte=end_date)
        
        # Show trash if requested
        if self.request.query_params.get('show_trash'):
            queryset = Booking.objects.filter(is_trash=True)
        
        return queryset.order_by('-created_at')


class BookingCalendarEventsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="رویدادهای تقویم رزرو",
        operation_description="دریافت رزروها به فرمت مناسب برای نمایش در تقویم"
    )
    def get(self, request):
        bookings = Booking.objects.select_related('room', 'primary_guest').filter(is_trash=False)
        
        # Generate room colors
        rooms = Room.objects.all()
        color_palette = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#EC4899', '#14B8A6', '#F97316', '#84CC16', '#06B6D4',
            '#6366F1', '#A855F7', '#D946EF', '#F43F5E', '#0EA5E9'
        ]
        room_colors = {room.id: color_palette[i % len(color_palette)] for i, room in enumerate(rooms)}
        
        events = []
        for booking in bookings:
            room_color = room_colors.get(booking.room_id, '#3B82F6')
            
            events.append({
                'id': booking.id,
                'title': f'Room {booking.room.number} - {booking.primary_guest.full_name}',
                'start': booking.check_in.isoformat(),
                'end': booking.check_out.isoformat(),
                'color': room_color,
                'extendedProps': {
                    'status': booking.status,
                    'room_number': booking.room.number,
                    'guest_name': booking.primary_guest.full_name,
                    'room_id': booking.room_id
                }
            })
        
        return Response(events)


# Guest Management Views
class GuestViewSet(ModelViewSet):
    queryset = Guest.objects.all().select_related('booking')
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="فهرست مهمانان",
        operation_description="دریافت لیست تمام مهمانان هتل",
        manual_parameters=[
            openapi.Parameter('booking', openapi.IN_QUERY, description="فیلتر بر اساس شناسه رزرو", type=openapi.TYPE_INTEGER),
            openapi.Parameter('primary_only', openapi.IN_QUERY, description="فقط مهمانان اصلی", type=openapi.TYPE_BOOLEAN),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="جزئیات مهمان",
        operation_description="دریافت جزئیات کامل یک مهمان خاص"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ایجاد مهمان",
        operation_description="ثبت مهمان جدید در سیستم"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش مهمان",
        operation_description="به‌روزرسانی اطلاعات یک مهمان"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="ویرایش بخشی از مهمان",
        operation_description="به‌روزرسانی بخشی از اطلاعات یک مهمان"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="حذف مهمان",
        operation_description="حذف یک مهمان از سیستم"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by booking
        booking_id = self.request.query_params.get('booking')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        
        # Filter primary guests only
        if self.request.query_params.get('primary_only'):
            queryset = queryset.filter(is_primary=True)
        
        return queryset


# Utility Views
@swagger_auto_schema(
    method='get',
    operation_summary="اتاق‌های در دسترس",
    operation_description="یافتن اتاق‌های خالی در بازه زمانی مشخص",
    manual_parameters=[
        openapi.Parameter('check_in', openapi.IN_QUERY, description="تاریخ ورود (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
        openapi.Parameter('check_out', openapi.IN_QUERY, description="تاریخ خروج (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
    ],
    responses={
        200: RoomSerializer(many=True),
        400: "پارامترهای نامعتبر"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_rooms(request):
    """Get available rooms for a date range"""
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if not check_in or not check_out:
        return Response({'error': 'check_in and check_out dates are required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Find rooms that are not booked during the requested period
    booked_rooms = Booking.objects.filter(
        check_out__gt=check_in_date,
        check_in__lt=check_out_date,
        status__in=['reserved', 'checked_in']
    ).values_list('room_id', flat=True)
    
    available_rooms = Room.objects.filter(
        status='available'
    ).exclude(id__in=booked_rooms)
    
    serializer = RoomSerializer(available_rooms, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    operation_summary="انتقال رزرو به سطل زباله",
    operation_description="حذف موقت یک رزرو (انتقال به سطل زباله)",
    responses={
        200: "رزرو با موفقیت به سطل زباله منتقل شد",
        404: "رزرو یافت نشد"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def soft_delete_booking(request, pk):
    """Soft delete a booking (move to trash)"""
    try:
        booking = Booking.objects.get(pk=pk)
        booking.is_trash = True
        booking.save()
        return Response({'message': 'Booking moved to trash successfully'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, 
                        status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='post',
    operation_summary="بازیابی رزرو از سطل زباله",
    operation_description="بازگرداندن یک رزرو از سطل زباله",
    responses={
        200: "رزرو با موفقیت بازیابی شد",
        404: "رزرو در سطل زباله یافت نشد"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_booking(request, pk):
    """Restore a booking from trash"""
    try:
        booking = Booking.objects.get(pk=pk, is_trash=True)
        booking.is_trash = False
        booking.save()
        return Response({'message': 'Booking restored successfully'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found in trash'}, 
                        status=status.HTTP_404_NOT_FOUND)