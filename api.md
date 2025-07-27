# API Documentation

## Authentication

### `POST /api/v1/auth/register/` - User registration

**توضیحات**: ثبت نام کاربر جدید در سیستم مدیریت هتل.
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "first_name": "نام",
  "last_name": "نام خانوادگی",
  "phone": "09123456789"
}
```

**پاسخ**:
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "نام",
    "last_name": "نام خانوادگی",
    "phone": "09123456789"
  },
  "token": "a3d4f5g6h7j8k9l0",
  "message": "Registration successful"
}
```

### `POST /api/v1/auth/login/` - User login

**توضیحات**: ورود کاربر به سیستم و دریافت توکن احراز هویت.
```json
{
  "username": "username",
  "password": "password123"
}
```
**پاسخ**:
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "نام",
    "last_name": "نام خانوادگی"
  },
  "token": "a3d4f5g6h7j8k9l0",
  "message": "Login successful"
}
```

### `POST /api/v1/auth/logout/` - User logout

**توضیحات**: خروج کاربر از سیستم و باطل کردن توکن.

**پاسخ**:
```json
{
  "message": "Logout successful"
}
```

### `GET/PUT /api/v1/auth/profile/` - User profile

**توضیحات**: مشاهده و ویرایش پروفایل کاربری.

**پاسخ GET**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "نام",
  "last_name": "نام خانوادگی",
  "phone": "09123456789",
  "date_joined": "2023-01-01T12:00:00Z"
}
```

## Dashboard

### `GET /api/v1/dashboard/stats/` - Dashboard statistics

**توضیحات**: آمار و اطلاعات کلی داشبورد مدیریتی هتل.

**پاسخ**:
```json
{
  "total": 50,
  "available": 30,
  "occupied": 15,
  "reserved": 5,
  "maintenance": 0,
  "total_bookings": 120,
  "todays_checkins": 5,
  "todays_checkouts": 3,
  "occupancy_rate": 40.0,
  "revenue_today": 5000000,
  "revenue_month": 150000000
}
```

## Rooms Management

### `GET /api/v1/rooms/` - List all rooms

**توضیحات**: فهرست تمام اتاق‌های هتل با امکان فیلتر کردن بر اساس وضعیت، طبقه و نوع اتاق.

**پاسخ**:
```json
[
  {
    "number": "101",
    "room_type": {
      "id": 1,
      "name": "اتاق استاندارد"
    },
    "floor": 1,
    "capacity": 2,
    "price": 500000.00,
    "status": "available",
    "view_type": "city",
    "balcony": false,
    "size_sqm": 25
  },
  // ...سایر اتاق‌ها
]
```

### `POST /api/v1/rooms/` - Create new room

**توضیحات**: ایجاد اتاق جدید در سیستم.

**پاسخ**: اطلاعات اتاق ایجاد شده.

### `GET /api/v1/rooms/{number}/` - Get room details

**توضیحات**: مشاهده جزئیات کامل یک اتاق خاص.

**پاسخ**:
```json
{
  "number": "101",
  "room_type": {
    "id": 1,
    "name": "اتاق استاندارد",
    "description": "اتاق راحت با امکانات اولیه"
  },
  "floor": 1,
  "capacity": 2,
  "price": 500000.00,
  "status": "available",
  "description": "اتاق زیبا در طبقه ۱ با نمای عالی",
  "size_sqm": 25,
  "view_type": "city",
  "balcony": false,
  "smoking_allowed": false,
  "last_maintenance": "2023-06-15",
  "next_maintenance": "2023-12-15",
  "amenities": [
    {
      "id": 1,
      "name": "تلویزیون",
      "icon": "ti-device-tv"
    },
    {
      "id": 2,
      "name": "اینترنت وای‌فای",
      "icon": "ti-wifi"
    }
    // ...سایر امکانات
  ]
}
```

### `PUT /api/v1/rooms/{number}/` - Update room

**توضیحات**: به‌روزرسانی اطلاعات یک اتاق.

**پاسخ**: اطلاعات به‌روز شده اتاق.

### `DELETE /api/v1/rooms/{number}/` - Delete room

**توضیحات**: حذف یک اتاق از سیستم.

**پاسخ**: تأیید حذف موفقیت‌آمیز.

### `GET /api/v1/rooms/available/` - Get available rooms for date range

**توضیحات**: یافتن اتاق‌های خالی در بازه زمانی مشخص.

**پارامترها**: `check_in`, `check_out`

**پاسخ**: لیست اتاق‌های در دسترس برای رزرو.

## Room Types

### `GET /api/v1/room-types/` - List room types

**توضیحات**: فهرست انواع اتاق‌های موجود در هتل.

**پاسخ**:
```json
[
  {
    "id": 1,
    "name": "اتاق استاندارد",
    "description": "اتاق راحت با امکانات اولیه",
    "base_price": 500000.00,
    "max_occupancy": 2,
    "size_sqm": 25,
    "room_count": 20,
    "available_room_count": 15
  },
  {
    "id": 2,
    "name": "اتاق دلوکس",
    "description": "اتاق بزرگتر با امکانات بیشتر",
    "base_price": 800000.00,
    "max_occupancy": 3,
    "size_sqm": 35,
    "room_count": 15,
    "available_room_count": 8
  }
  // ...سایر انواع اتاق
]
```

### `POST /api/v1/room-types/` - Create room type

**توضیحات**: ایجاد نوع اتاق جدید.

**پاسخ**: اطلاعات نوع اتاق ایجاد شده.

### `GET /api/v1/room-types/{id}/` - Get room type details

**توضیحات**: مشاهده جزئیات کامل یک نوع اتاق خاص.

**پاسخ**: اطلاعات کامل نوع اتاق به همراه امکانات پیش‌فرض.

### `PUT /api/v1/room-types/{id}/` - Update room type

**توضیحات**: به‌روزرسانی اطلاعات یک نوع اتاق.

**پاسخ**: اطلاعات به‌روز شده نوع اتاق.

### `DELETE /api/v1/room-types/{id}/` - Delete room type

**توضیحات**: حذف یک نوع اتاق از سیستم.

**پاسخ**: تأیید حذف موفقیت‌آمیز.

## Amenities

### `GET /api/v1/amenities/` - List amenities

**توضیحات**: فهرست تمام امکانات قابل ارائه در اتاق‌های هتل.

**پاسخ**:
```json
[
  {
    "id": 1,
    "name": "تلویزیون",
    "icon": "ti-device-tv",
    "category": "basic",
    "is_chargeable": false,
    "extra_charge": 0.00
  },
  {
    "id": 2,
    "name": "جکوزی",
    "icon": "ti-ripple",
    "category": "luxury",
    "is_chargeable": true,
    "extra_charge": 200000.00
  }
  // ...سایر امکانات
]
```

### `POST /api/v1/amenities/` - Create amenity

**توضیحات**: ایجاد امکان جدید برای اتاق‌ها.

**پاسخ**: اطلاعات امکان ایجاد شده.

### `GET /api/v1/amenities/{id}/` - Get amenity details

**توضیحات**: مشاهده جزئیات کامل یک امکان خاص.

**پاسخ**: اطلاعات کامل امکان.

### `PUT /api/v1/amenities/{id}/` - Update amenity

**توضیحات**: به‌روزرسانی اطلاعات یک امکان.

**پاسخ**: اطلاعات به‌روز شده امکان.

### `DELETE /api/v1/amenities/{id}/` - Delete amenity

**توضیحات**: حذف یک امکان از سیستم.

**پاسخ**: تأیید حذف موفقیت‌آمیز.

## Bookings

### `GET /api/v1/bookings/` - List bookings

**توضیحات**: فهرست تمام رزروهای هتل با امکان فیلتر کردن.

**پاسخ**:
```json
[
  {
    "id": 1,
    "booking_reference": "BK-20230715-A123",
    "room": {
      "number": "101",
      "room_type": "اتاق استاندارد"
    },
    "check_in": "2023-07-20",
    "check_out": "2023-07-25",
    "status": "reserved",
    "primary_guest": {
      "id": 1,
      "full_name": "علی محمدی",
      "phone": "09123456789"
    },
    "total_amount": 2500000.00,
    "payment_status": "partial"
  }
  // ...سایر رزروها
]
```

### `POST /api/v1/bookings/` - Create booking

**توضیحات**: ایجاد رزرو جدید در سیستم.

**پاسخ**: اطلاعات رزرو ایجاد شده.

### `GET /api/v1/bookings/{id}/` - Get booking details

**توضیحات**: مشاهده جزئیات کامل یک رزرو خاص.

**پاسخ**:
```json
{
  "id": 1,
  "booking_reference": "BK-20230715-A123",
  "room": {
    "number": "101",
    "room_type": "اتاق استاندارد",
    "price": 500000.00
  },
  "check_in": "2023-07-20",
  "check_out": "2023-07-25",
  "status": "reserved",
  "primary_guest": {
    "id": 1,
    "national_id": "0123456789",
    "first_name": "علی",
    "last_name": "محمدی",
    "phone": "09123456789",
    "email": "ali@example.com"
  },
  "assigned_staff": {
    "id": 2,
    "full_name": "رضا حسینی"
  },
  "adults": 2,
  "children": 1,
  "special_requests": "اتاق در طبقات بالا",
  "room_rate": 500000.00,
  "total_amount": 2500000.00,
  "discount_amount": 0.00,
  "tax_amount": 225000.00,
  "payment_status": "partial",
  "advance_payment": 1000000.00,
  "booking_source": "website",
  "early_check_in": false,
  "late_check_out": false,
  "created_at": "2023-07-15T14:30:00Z"
}
```

### `PUT /api/v1/bookings/{id}/` - Update booking

**توضیحات**: به‌روزرسانی اطلاعات یک رزرو.

**پاسخ**: اطلاعات به‌روز شده رزرو.


### `DELETE /api/v1/bookings/{id}/` - Delete booking

**توضیحات**: حذف یک رزرو از سیستم.

**پاسخ**: تأیید حذف موفقیت‌آمیز.

### `GET /api/v1/bookings/calendar/events/` - Calendar events

**توضیحات**: دریافت رویدادهای تقویم برای نمایش در تقویم رزروها.

**پاسخ**:
```json
[
  {
    "id": 1,
    "title": "Room 101 - علی محمدی",
    "start": "2023-07-20",
    "end": "2023-07-25",
    "color": "#3B82F6",
    "extendedProps": {
      "status": "reserved",
      "room_number": "101",
      "guest_name": "علی محمدی",
      "room_id": 5
    }
  }
  // ...سایر رویدادها
]
```

### `POST /api/v1/bookings/{id}/soft-delete/` - Soft delete booking

**توضیحات**: انتقال یک رزرو به سطل زباله بدون حذف کامل.

**پاسخ**:
```json
{
  "message": "Booking moved to trash successfully"
}
```


### `POST /api/v1/bookings/{id}/restore/` - Restore booking

**توضیحات**: بازیابی یک رزرو از سطل زباله.

**پاسخ**:
```json
{
  "message": "Booking restored successfully"
}
```

## Guests

### `GET /api/v1/guests/` - List guests

**توضیحات**: فهرست تمام مهمانان ثبت شده در سیستم.

**پاسخ**:
```json
[
  {
    "id": 1,
    "national_id": "0123456789",
    "first_name": "علی",
    "last_name": "محمدی",
    "full_name": "علی محمدی",
    "phone": "09123456789",
    "email": "ali@example.com",
    "nationality": "ایرانی",
    "is_primary": true,
    "booking": 1
  }
  // ...سایر مهمانان
]
```

### `POST /api/v1/guests/` - Create guest

**توضیحات**: ثبت مهمان جدید در سیستم.

**پاسخ**: اطلاعات مهمان ایجاد شده.

### `GET /api/v1/guests/{id}/` - Get guest details

**توضیحات**: مشاهده جزئیات کامل یک مهمان خاص.

**پاسخ**:
```json
{
  "id": 1,
  "national_id": "0123456789",
  "first_name": "علی",
  "last_name": "محمدی",
  "full_name": "علی محمدی",
  "gender": "M",
  "phone": "09123456789",
  "email": "ali@example.com",
  "address": "تهران، خیابان ولیعصر",
  "date_of_birth": "1980-05-15",
  "nationality": "ایرانی",
  "passport_number": "",
  "booking": {
    "id": 1,
    "booking_reference": "BK-20230715-A123"
  },
  "is_primary": true,
  "created_at": "2023-07-15T14:30:00Z"
}
```

### `PUT /api/v1/guests/{id}/` - Update guest

**توضیحات**: به‌روزرسانی اطلاعات یک مهمان.

**پاسخ**: اطلاعات به‌روز شده مهمان.

### `DELETE /api/v1/guests/{id}/` - Delete guest

**توضیحات**: حذف یک مهمان از سیستم.

**پاسخ**: تأیید حذف موفقیت‌آمیز.

## Reports

### `GET /api/v1/reports/` - List available reports

**توضیحات**: فهرست گزارش‌های قابل دسترسی در سیستم.

**پاسخ**:
```json
{
  "occupancy": "http://127.0.0.1:8000/api/v1/reports/occupancy/",
  "bookings": "http://127.0.0.1:8000/api/v1/reports/bookings/",
  "guests": "http://127.0.0.1:8000/api/v1/reports/guests/",
  "staff": "http://127.0.0.1:8000/api/v1/reports/staff/"
}
```

### `GET /api/v1/reports/occupancy/` - Hotel occupancy stats

**توضیحات**: گزارش آمار اشغال هتل و وضعیت اتاق‌ها.

**پاسخ**:
```json
{
  "total_rooms": 50,
  "occupied_rooms": 15,
  "reserved_rooms": 5,
  "available_rooms": 30,
  "occupancy_rate": 40.0
}
```

### `GET /api/v1/reports/bookings/` - Bookings stats

**توضیحات**: گزارش آمار رزروها در بازه‌های زمانی مختلف.

**پاسخ**:
```json
{
  "total_bookings": 120,
  "bookings_in_period": 35,
  "average_stay_length": 3.5,
  "most_booked_room_types": [
    {"name": "اتاق دلوکس", "count": 45},
    {"name": "اتاق استاندارد", "count": 40},
    {"name": "سوئیت جونیور", "count": 25}
  ],
  "booking_sources": [
    {"source": "website", "count": 60},
    {"source": "phone", "count": 30},
    {"source": "walk_in", "count": 20},
    {"source": "agent", "count": 10}
  ]
}
```

### `GET /api/v1/reports/guests/` - Guest stats

**توضیحات**: گزارش آمار و اطلاعات مهمانان.

**پاسخ**:
```json
{
  "total_guests": 250,
  "repeat_guests": 45,
  "guest_nationalities": [
    {"nationality": "ایرانی", "count": 200},
    {"nationality": "عراقی", "count": 25},
    {"nationality": "ترکیه‌ای", "count": 15},
    {"nationality": "سایر", "count": 10}
  ],
  "average_guest_age": 38.5
}
```

### `GET /api/v1/reports/staff/` - Staff activity

**توضیحات**: گزارش فعالیت‌های کارکنان هتل.

**پاسخ**:
```json
{
  "total_staff": 15,
  "bookings_per_staff": [
    {"staff_name": "رضا حسینی", "bookings_count": 45},
    {"staff_name": "زهرا محمدی", "bookings_count": 38},
    {"staff_name": "علی کریمی", "bookings_count": 25}
  ]
}
```

## Settings

### `GET /api/v1/settings/` - List settings endpoints

**توضیحات**: فهرست تنظیمات قابل دسترسی در سیستم.

**پاسخ**:
```json
{
  "settings": "http://127.0.0.1:8000/api/v1/settings/1/"
}
```

### `GET /api/v1/settings/1/` - Get global hotel settings

**توضیحات**: دریافت تنظیمات کلی هتل.

**پاسخ**:
```json
{
  "site_name": "هتل پرشیا",
  "logo": "http://127.0.0.1:8000/media/settings/logo.png",
  "address": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
  "phone": "021-12345678",
  "email": "info@hotelpersia.com",
  "tax_rate": 9.0,
  "currency": "IRR"
}
```

### `PUT /api/v1/settings/1/` - Update global hotel settings

**توضیحات**: به‌روزرسانی تنظیمات کلی هتل.

**پاسخ**: اطلاعات به‌روز شده تنظیمات.
