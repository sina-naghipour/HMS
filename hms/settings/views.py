from django.shortcuts import render
from django.views import View
from rest_framework.response import Response



class General(View):
    template_name = 'settings/general.html'
    def get(self, request):
        return render(request, self.template_name)


class Payment(View):
    template_name = 'settings/payment.html'
    def get(self, request):
        return render(request, self.template_name)



class Email(View):
    template_name = 'settings/email.html'
    def get(self, request):
        return render(request, self.template_name)

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from .models import HotelSettings
from .serializers import HotelSettingsSerializer

class SettingsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = HotelSettings.objects.all()
    serializer_class = HotelSettingsSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="فهرست تنظیمات",
        operation_description="دریافت لیست تنظیمات قابل دسترسی"
    )
    def list(self, request):
        return Response({
            "settings": request.build_absolute_uri('1/')
        })

    @swagger_auto_schema(
        operation_summary="دریافت تنظیمات هتل",
        operation_description="دریافت تنظیمات کلی هتل"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="به‌روزرسانی تنظیمات هتل",
        operation_description="به‌روزرسانی تنظیمات کلی هتل"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="به‌روزرسانی بخشی از تنظیمات هتل",
        operation_description="به‌روزرسانی بخشی از تنظیمات کلی هتل"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_object(self):
        # Singleton pattern: always return pk=1
        return HotelSettings.load()