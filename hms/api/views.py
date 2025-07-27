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

    def get_object(self):
        return self.request.user


# Dashboard Views
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

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


class AmenityViewSet(ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticated]




class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all().select_related('room', 'primary_guest', 'assigned_staff')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        return BookingSerializer

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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to create booking',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'error': 'Failed to update booking',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class BookingCalendarEventsView(APIView):
    permission_classes = [IsAuthenticated]

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