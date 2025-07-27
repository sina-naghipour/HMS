from rest_framework import serializers
from .models import HotelSettings

class HotelSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelSettings
        fields = '__all__'