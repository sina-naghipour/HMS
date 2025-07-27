import os
import sys
import django
import random
from datetime import datetime, timedelta, date
from decimal import Decimal
from faker import Faker
from faker.providers import BaseProvider
from django.utils import timezone

# Set up Django environment
sys.path.append('D:/codes/Hotel-HMS/HMS/hms')  # Adjust this path as needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms.settings')
django.setup()

# Import your models
from accounts.models import CustomUser
from guests.models import Guest
from rooms.models import Room, RoomType, Amenity
from bookings.models import Booking

# Create Faker instance with Persian locale
fake = Faker('fa_IR')
fake_en = Faker('en_US')  # For some English data like emails

# Custom provider for Persian names and data
class PersianProvider(BaseProvider):
    first_names_male = [
        'علی', 'محمد', 'حسین', 'رضا', 'احمد', 'حسن', 'مهدی', 'امیر', 'سعید', 'محسن',
        'جواد', 'کریم', 'مجید', 'میلاد', 'پیمان', 'سینا', 'آرش', 'فرهاد', 'بهزاد', 'داود'
    ]
    
    first_names_female = [
        'فاطمه', 'زهرا', 'مریم', 'زینب', 'سارا', 'نرگس', 'الهام', 'نازنین', 'شیما', 'لیلا',
        'آزاده', 'مینا', 'شهلا', 'پریسا', 'نیلوفر', 'یاسمین', 'رویا', 'شیرین', 'گلناز', 'سمیرا'
    ]
    
    last_names = [
        'محمدی', 'احمدی', 'رضایی', 'حسینی', 'علیزاده', 'کریمی', 'جعفری', 'نوری', 'صادقی', 'موسوی',
        'اکبری', 'امینی', 'رحیمی', 'زارعی', 'کاظمی', 'قاسمی', 'نجفی', 'حیدری', 'بابایی', 'یزدی'
    ]
    
    cities = [
        'تهران', 'مشهد', 'اصفهان', 'کرج', 'شیراز', 'تبریز', 'قم', 'اهواز', 'کرمانشاه', 'ارومیه',
        'رشت', 'زاهدان', 'همدان', 'کرمان', 'یزد', 'اردبیل', 'بندرعباس', 'اراک', 'قزوین', 'زنجان'
    ]
    
    def persian_first_name_male(self):
        return self.random_element(self.first_names_male)
    
    def persian_first_name_female(self):
        return self.random_element(self.first_names_female)
    
    def persian_last_name(self):
        return self.random_element(self.last_names)
    
    def persian_city(self):
        return self.random_element(self.cities)
    
    def persian_phone(self):
        prefixes = ['0912', '0913', '0914', '0915', '0916', '0917', '0918', '0919', '0990', '0991']
        return f"{self.random_element(prefixes)}{self.random_int(1000000, 9999999)}"
    
    def persian_national_id(self):
        # Generate a 10-digit national ID
        return str(self.random_int(1000000000, 9999999999))

# Add custom provider to faker
fake.add_provider(PersianProvider)

def clear_existing_data():
    print("Clearing existing data...")
    Guest.objects.all().delete()      # Delete guests first
    Booking.objects.all().delete()    # Then bookings
    Room.objects.all().delete()
    RoomType.objects.all().delete()
    Amenity.objects.all().delete()
    CustomUser.objects.exclude(email='style.npr@gmail.com').delete()

def create_amenities():
    """Create amenities"""
    print("Creating amenities...")
    amenities_data = [
        # Basic amenities
        {'name': 'تلویزیون', 'icon': 'ti-device-tv', 'category': 'basic', 'is_chargeable': False},
        {'name': 'اینترنت وای‌فای', 'icon': 'ti-wifi', 'category': 'basic', 'is_chargeable': False},
        {'name': 'تهویه مطبوع', 'icon': 'ti-air-conditioning', 'category': 'basic', 'is_chargeable': False},
        {'name': 'یخچال', 'icon': 'ti-fridge', 'category': 'basic', 'is_chargeable': False},
        {'name': 'گاوصندوق', 'icon': 'ti-safe', 'category': 'basic', 'is_chargeable': False},
        
        # Entertainment
        {'name': 'نتفلیکس', 'icon': 'ti-brand-netflix', 'category': 'entertainment', 'is_chargeable': True, 'extra_charge': Decimal('50000')},
        {'name': 'پلی‌استیشن', 'icon': 'ti-device-gamepad', 'category': 'entertainment', 'is_chargeable': True, 'extra_charge': Decimal('100000')},
        
        # Business
        {'name': 'میز کار', 'icon': 'ti-desk', 'category': 'business', 'is_chargeable': False},
        {'name': 'پرینتر', 'icon': 'ti-printer', 'category': 'business', 'is_chargeable': True, 'extra_charge': Decimal('30000')},
        
        # Luxury
        {'name': 'جکوزی', 'icon': 'ti-ripple', 'category': 'luxury', 'is_chargeable': True, 'extra_charge': Decimal('200000')},
        {'name': 'مینی بار', 'icon': 'ti-glass-cocktail', 'category': 'luxury', 'is_chargeable': True, 'extra_charge': Decimal('150000')},
        {'name': 'بالکن', 'icon': 'ti-home-2', 'category': 'luxury', 'is_chargeable': False},
    ]
    
    amenities = []
    for data in amenities_data:
        amenity, _ = Amenity.objects.get_or_create(**data)
        amenities.append(amenity)
    
    return amenities

def create_room_types():
    """Create room types"""
    print("Creating room types...")
    room_types_data = [
        {
            'name': 'اتاق استاندارد',
            'description': 'اتاق راحت با امکانات اولیه',
            'base_price': Decimal('500000'),
            'max_occupancy': 2,
            'size_sqm': 25
        },
        {
            'name': 'اتاق دلوکس',
            'description': 'اتاق بزرگتر با امکانات بیشتر',
            'base_price': Decimal('800000'),
            'max_occupancy': 3,
            'size_sqm': 35
        },
        {
            'name': 'سوئیت جونیور',
            'description': 'سوئیت کوچک با فضای نشیمن',
            'base_price': Decimal('1200000'),
            'max_occupancy': 4,
            'size_sqm': 45
        },
        {
            'name': 'سوئیت اجرایی',
            'description': 'سوئیت بزرگ با امکانات کامل',
            'base_price': Decimal('2000000'),
            'max_occupancy': 4,
            'size_sqm': 60
        },
        {
            'name': 'سوئیت رویال',
            'description': 'بهترین سوئیت با نمای عالی',
            'base_price': Decimal('3500000'),
            'max_occupancy': 6,
            'size_sqm': 100
        }
    ]
    
    room_types = []
    amenities = list(Amenity.objects.all())
    
    for data in room_types_data:
        room_type, _ = RoomType.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        # Add some default amenities based on room type
        if 'استاندارد' in room_type.name:
            room_type.default_amenities.set(random.sample(amenities[:5], 3))
        elif 'دلوکس' in room_type.name:
            room_type.default_amenities.set(random.sample(amenities[:8], 5))
        else:  # Suites
            room_type.default_amenities.set(random.sample(amenities, 8))
        
        room_types.append(room_type)
    
    return room_types

def create_rooms():
    """Create rooms"""
    print("Creating rooms...")
    room_types = RoomType.objects.all()
    rooms = []
    
    floors = 10  # 10 floors
    rooms_per_floor = 15
    
    for floor in range(1, floors + 1):
        for room_num in range(1, rooms_per_floor + 1):
            room_number = f"{floor}{room_num:02d}"
            # Avoid duplicate room numbers in case script is run again
            if Room.objects.filter(number=room_number).exists():
                continue
            # Assign room types based on floor
            if floor <= 3:
                room_type = random.choice(room_types.filter(name__contains='استاندارد'))
            elif floor <= 6:
                room_type = random.choice(room_types.filter(name__in=['اتاق استاندارد', 'اتاق دلوکس']))
            elif floor <= 8:
                room_type = random.choice(room_types.filter(name__in=['اتاق دلوکس', 'سوئیت جونیور']))
            else:
                room_type = random.choice(room_types.exclude(name='اتاق استاندارد'))
            
            # Set price variation
            price_variation = random.uniform(0.9, 1.2)
            price = room_type.base_price * Decimal(str(price_variation))
            
            # Determine view based on floor and room number
            if floor >= 8:
                view_choices = ['city', 'mountain', 'ocean']
            elif floor >= 5:
                view_choices = ['city', 'garden', 'pool']
            else:
                view_choices = ['garden', 'courtyard', 'pool']
            
            room = Room.objects.create(
                number=room_number,
                room_type=room_type,
                floor=floor,
                capacity=random.randint(room_type.max_occupancy - 1, room_type.max_occupancy),
                price=price,
                status=random.choice(['available', 'available', 'available', 'occupied', 'maintenance']),
                description=f"اتاق زیبا در طبقه {floor} با نمای عالی",
                size_sqm=room_type.size_sqm + random.randint(-5, 10),
                view_type=random.choice(view_choices),
                balcony=floor >= 5 and random.choice([True, False]),
                smoking_allowed=random.choice([True, False, False]),  # Most rooms non-smoking
                last_maintenance=fake.date_between(start_date='-6m', end_date='today'),
            )
            
            # Set next maintenance
            room.next_maintenance = room.last_maintenance + timedelta(days=random.randint(90, 180))
            room.save()
            
            # Add amenities
            room.amenities.set(room_type.default_amenities.all())
            # Add some random extra amenities
            extra_amenities = Amenity.objects.exclude(
                id__in=room_type.default_amenities.values_list('id', flat=True)
            )
            if extra_amenities:
                room.amenities.add(*random.sample(list(extra_amenities), min(3, extra_amenities.count())))
            
            rooms.append(room)
    
    return rooms

def create_staff_users():
    """Create staff users"""
    print("Creating staff users...")
    staff_users = []
    
    # Create reception staff
    for i in range(5):
        gender = random.choice(['M', 'F'])
        if gender == 'M':
            first_name = fake.persian_first_name_male()
        else:
            first_name = fake.persian_first_name_female()
        
        last_name = fake.persian_last_name()
        username = f"staff_{fake_en.user_name()}"
        
        user = CustomUser.objects.create_user(
            email=f"{username}@hotelpersia.com",
            username=username,
            password='toor',
            first_name=first_name,
            last_name=last_name,
            phone=fake.persian_phone(),
            is_staff=True
        )
        staff_users.append(user)
    
    return staff_users

def create_guests_and_bookings():
    """Create guests and bookings"""
    print("Creating guests and bookings...")
    
    rooms = Room.objects.filter(status='available')
    staff_users = CustomUser.objects.filter(is_staff=True)
    
    # Create bookings for the past 6 months and future 3 months
    start_date = date.today() - timedelta(days=180)
    end_date = date.today() + timedelta(days=90)
    
    booking_count = 0
    
    while booking_count < 200:  # Create 200 bookings
        # 1. Create primary guest WITHOUT is_primary and booking
        gender = random.choice(['M', 'F'])
        if gender == 'M':
            first_name = fake.persian_first_name_male()
        else:
            first_name = fake.persian_first_name_female()
        
        primary_guest = Guest.objects.create(
            national_id=fake.persian_national_id(),
            first_name=first_name,
            last_name=fake.persian_last_name(),
            gender=gender,
            phone=fake.persian_phone(),
            email=fake_en.email(),
            address=f"{fake.street_address()}, {fake.persian_city()}",
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            nationality='ایرانی',
            is_primary=False,
            booking=None
        )
        
        # Select random room
        room = random.choice(rooms)
        
        # Generate check-in and check-out dates
        check_in = fake.date_between(start_date=start_date, end_date=end_date)
        nights = random.randint(1, 7)
        check_out = check_in + timedelta(days=nights)
        
        # Determine status based on dates
        today = date.today()
        if check_out < today:
            status = 'checked_out'
        elif check_in <= today < check_out:
            status = random.choice(['checked_in', 'reserved'])
        else:
            status = random.choice(['reserved', 'confirmed'])
        
        # Calculate pricing
        room_rate = room.price
        discount_percent = random.choice([0, 0, 0, 5, 10, 15])  # Most bookings no discount
        discount_amount = room_rate * nights * Decimal(discount_percent / 100)
        tax_rate = Decimal('0.09')  # 9% tax
        subtotal = room_rate * nights - discount_amount
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Payment status
        if status == 'checked_out':
            payment_status = 'paid'
            advance_payment = total_amount
        elif status == 'checked_in':
            payment_status = random.choice(['paid', 'partial'])
            if payment_status == 'partial':
                advance_payment = total_amount * Decimal('0.5')
            else:
                advance_payment = total_amount
        else:
            payment_status = random.choice(['pending', 'partial'])
            if payment_status == 'partial':
                advance_payment = total_amount * Decimal('0.3')
            else:
                advance_payment = Decimal('0')
        
        # Create booking with this guest as primary
        booking = Booking.objects.create(
            room=room,
            check_in=check_in,
            check_out=check_out,
            status=status,
            primary_guest=primary_guest,
            assigned_staff=random.choice(staff_users),
            adults=random.randint(1, room.capacity),
            children=random.randint(0, min(2, room.capacity - 1)),
            special_requests=random.choice([
                '',
                'اتاق در طبقات بالا',
                'تخت اضافه برای کودک',
                'اتاق دور از آسانسور',
                'نمای دریا',
                'اتاق ضد سیگار'
            ]),
            room_rate=room_rate,
            total_amount=total_amount,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            payment_status=payment_status,
            advance_payment=advance_payment,
            booking_source=random.choice(['direct', 'phone', 'website', 'walk_in', 'agent']),
            early_check_in=random.choice([True, False, False, False]),
            late_check_out=random.choice([True, False, False, False]),
        )
        
        # Now update the primary guest: assign booking and set is_primary to True
        primary_guest.booking = booking
        primary_guest.is_primary = True
        primary_guest.save()
        
        if status in ['checked_in', 'checked_out']:
            dt_in = datetime.combine(check_in, datetime.min.time()) + timedelta(hours=random.randint(12, 18))
            booking.actual_check_in = timezone.make_aware(dt_in)

            if status == 'checked_out':
                dt_out = datetime.combine(check_out, datetime.min.time()) + timedelta(hours=random.randint(10, 14))
                booking.actual_check_out = timezone.make_aware(dt_out)
            booking.save()
        
        # Add additional guests for some bookings
        if booking.adults > 1 and random.choice([True, False]):
            for i in range(booking.adults - 1):
                gender = random.choice(['M', 'F'])
                if gender == 'M':
                    first_name = fake.persian_first_name_male()
                else:
                    first_name = fake.persian_first_name_female()
                
                Guest.objects.create(
                    national_id=fake.persian_national_id(),
                    first_name=first_name,
                    last_name=fake.persian_last_name(),
                    gender=gender,
                    phone=fake.persian_phone(),
                    email=fake_en.email() if random.choice([True, False]) else '',
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
                    nationality='ایرانی',
                    booking=booking,
                    is_primary=False
                )
        
        booking_count += 1
        
        if booking_count % 50 == 0:
            print(f"Created {booking_count} bookings...")
    
    # Update room statuses based on current bookings
    for room in Room.objects.all():
        current_booking = room.get_current_booking()
        if current_booking:
            if current_booking.status == 'checked_in':
                room.status = 'occupied'
            elif current_booking.status in ['reserved', 'confirmed']:
                room.status = 'reserved'
            room.save()

def main():
    print("Starting fake data generation...")
    print("=" * 50)
    clear_existing_data()  # Always clear before generating!
    create_amenities()
    create_room_types()
    create_rooms()
    create_staff_users()
    create_guests_and_bookings()
    print("=" * 50)
    print("Data generation completed!")
    print(f"Created:")
    print(f"- {Amenity.objects.count()} amenities")
    print(f"- {RoomType.objects.count()} room types")
    print(f"- {Room.objects.count()} rooms")
    print(f"- {CustomUser.objects.filter(is_staff=True).count()} staff users")
    print(f"- {Guest.objects.count()} guests")
    print(f"- {Booking.objects.count()} bookings")


if __name__ == "__main__":
    main()
