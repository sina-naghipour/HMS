from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import CustomUser
from rooms.models import Room, RoomType, Amenity
from bookings.models import Booking
from guests.models import Guest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'is_staff', 'is_active', 'date_joined', 'password', 'password_confirm')
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'


class RoomTypeSerializer(serializers.ModelSerializer):
    default_amenities = AmenitySerializer(many=True, read_only=True)
    room_count = serializers.ReadOnlyField()
    min_price = serializers.ReadOnlyField()
    max_price = serializers.ReadOnlyField()

    class Meta:
        model = RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    room_type = RoomTypeSerializer(read_only=True)
    room_type_id = serializers.IntegerField(write_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    amenity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Room
        fields = '__all__'

    def create(self, validated_data):
        amenity_ids = validated_data.pop('amenity_ids', [])
        room = Room.objects.create(**validated_data)
        if amenity_ids:
            room.amenities.set(amenity_ids)
        return room

    def update(self, instance, validated_data):
        amenity_ids = validated_data.pop('amenity_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if amenity_ids is not None:
            instance.amenities.set(amenity_ids)
        
        return instance


class GuestSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Guest
        fields = '__all__'



class BookingSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    room_id = serializers.IntegerField(write_only=True)
    primary_guest = GuestSerializer(read_only=True)
    assigned_staff = CustomUserSerializer(read_only=True)
    nights = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    # Guest information for creation
    guest_data = serializers.JSONField(write_only=True, required=False)
    additional_guests = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('assigned_staff', 'created_at', 'updated_at')

    def validate(self, attrs):
        check_in = attrs.get('check_in')
        check_out = attrs.get('check_out')
        room_id = attrs.get('room_id')

        # Enhanced date validation
        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError({
                    'check_out': 'Check-out date must be after check-in date'
                })
            
            # Check if check-in is not in the past
            from django.utils import timezone
            if check_in < timezone.now().date():
                raise serializers.ValidationError({
                    'check_in': 'Check-in date cannot be in the past'
                })
            
            # Check minimum stay (optional)
            if (check_out - check_in).days < 1:
                raise serializers.ValidationError({
                    'check_out': 'Minimum stay is 1 night'
                })

        # Check for conflicting bookings
        if room_id and check_in and check_out:
            conflicting = Booking.objects.filter(
                room_id=room_id,
                check_out__gt=check_in,
                check_in__lt=check_out,
                status__in=['reserved', 'checked_in'],
                is_trash=False  # Don't consider trashed bookings
            )
            
            # Exclude current instance if updating
            if self.instance:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            
            if conflicting.exists():
                raise serializers.ValidationError({
                    'room_id': 'Room is already booked for these dates'
                })

        return attrs

    def create(self, validated_data):
        guest_data = validated_data.pop('guest_data', {})
        additional_guests = validated_data.pop('additional_guests', [])
        
        # Validate guest data
        if not guest_data:
            raise serializers.ValidationError({
                'guest_data': 'Primary guest information is required'
            })
        
        # Create primary guest
        try:
            primary_guest = Guest.objects.create(**guest_data, is_primary=True)
        except Exception as e:
            raise serializers.ValidationError({
                'guest_data': f'Error creating guest: {str(e)}'
            })
        
        validated_data['primary_guest'] = primary_guest
        
        # Set assigned staff from request
        request = self.context.get('request')
        if request and request.user:
            validated_data['assigned_staff'] = request.user

        try:
            booking = Booking.objects.create(**validated_data)
        except Exception as e:
            # Clean up the guest if booking creation fails
            primary_guest.delete()
            raise serializers.ValidationError({
                'non_field_errors': f'Error creating booking: {str(e)}'
            })
        
        # Update primary guest with booking reference
        primary_guest.booking = booking
        primary_guest.save()
        
        # Create additional guests
        for guest_info in additional_guests:
            try:
                Guest.objects.create(**guest_info, booking=booking, is_primary=False)
            except Exception as e:
                # Log the error but don't fail the entire booking
                print(f"Error creating additional guest: {e}")
        
        return booking



class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing bookings"""
    room_number = serializers.CharField(source='room.number', read_only=True)
    guest_name = serializers.CharField(source='primary_guest.full_name', read_only=True)
    nights = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ('id', 'room_number', 'guest_name', 'check_in', 'check_out', 
                 'status', 'nights', 'total_price', 'created_at')


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    reserved_rooms = serializers.IntegerField()
    maintenance_rooms = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    todays_checkins = serializers.IntegerField()
    todays_checkouts = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    revenue_today = serializers.FloatField()
    revenue_month = serializers.FloatField()