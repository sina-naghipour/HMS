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
from bookings.models import Booking
from rooms.models import Room
from guests.models import Guest

class ReportsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

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

    @action(detail=False, methods=['get'])
    def bookings(self, request):
        total_bookings = Booking.objects.count()
        return Response({"total_bookings": total_bookings})

    @action(detail=False, methods=['get'])
    def guests(self, request):
        total_guests = Guest.objects.count()
        return Response({"total_guests": total_guests})
    from rest_framework.response import Response
from rest_framework import viewsets

class ReportsViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({
            "occupancy": request.build_absolute_uri('occupancy/'),
            "bookings": request.build_absolute_uri('bookings/'),
            "guests": request.build_absolute_uri('guests/'),
        })
        