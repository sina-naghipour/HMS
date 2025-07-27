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
from .models import HotelSettings
from .serializers import HotelSettingsSerializer
from rest_framework.permissions import IsAdminUser

class SettingsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = HotelSettings.objects.all()
    serializer_class = HotelSettingsSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        # Singleton pattern: always return pk=1
        return HotelSettings.load()
    def list(self, request):
        return Response({
            "settings": request.build_absolute_uri('1/')
        })