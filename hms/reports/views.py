from django.shortcuts import render
from django.views import View


class Occupancy(View):
    template_name = 'reports/occupancy.html'
    def get(self, request):
        return render(request, self.template_name)


class Revenue(View):
    template_name = 'reports/revenue.html'
    def get(self, request):
        return render(request, self.template_name)


class Custom(View):
    template_name = 'reports/custom.html'
    def get(self, request):
        return render(request, self.template_name)

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from bookings.models import Booking
from rooms.models import Room
from guests.models import Guest

class ReportsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="فهرست گزارش‌ها",
        operation_description="دریافت لیست تمام گزارش‌های قابل دسترسی"
    )
    def list(self, request):
        return Response({
            "occupancy": request.build_absolute_uri('occupancy/'),
            "bookings": request.build_absolute_uri('bookings/'),
            "guests": request.build_absolute_uri('guests/'),
            "staff": request.build_absolute_uri('staff/')
        })

    @swagger_auto_schema(
        operation_summary="آمار اشغال هتل",
        operation_description="گزارش آمار اشغال هتل و وضعیت اتاق‌ها"
    )
    @action(detail=False, methods=['get'])
    def occupancy(self, request):
        total_rooms = Room.objects.count()
        occupied_rooms = Room.objects.filter(status='occupied').count()
        reserved_rooms = Room.objects.filter(status='reserved').count()
        available_rooms = Room.objects.filter(status='available').count()
        return Response({
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "reserved_rooms": reserved_rooms,
            "available_rooms": available_rooms,
            "occupancy_rate": round(occupied_rooms / total_rooms * 100, 2) if total_rooms else 0,
        })

    @swagger_auto_schema(
        operation_summary="آمار رزروها",
        operation_description="گزارش آمار رزروها در بازه‌های زمانی مختلف",
        manual_parameters=[
            openapi.Parameter('start', openapi.IN_QUERY, description="تاریخ شروع بازه (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end', openapi.IN_QUERY, description="تاریخ پایان بازه (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    @action(detail=False, methods=['get'])
    def bookings(self, request):
        total_bookings = Booking.objects.count()
        return Response({"total_bookings": total_bookings})

    @swagger_auto_schema(
        operation_summary="آمار مهمانان",
        operation_description="گزارش آمار و اطلاعات مهمانان هتل"
    )
    @action(detail=False, methods=['get'])
    def guests(self, request):
        total_guests = Guest.objects.count()
        return Response({"total_guests": total_guests})

    @swagger_auto_schema(
        operation_summary="آمار فعالیت کارکنان",
        operation_description="گزارش فعالیت‌های کارکنان هتل"
    )
    @action(detail=False, methods=['get'])
    def staff(self, request):
        # Your staff report logic here
        return Response({"total_staff": 0})