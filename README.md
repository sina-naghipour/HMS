<div dir="rtl" align="right">

# سیستم مدیریت هتل (HMS)

![هتل](https://via.placeholder.com/800x200/3498db/ffffff?text=سیستم+مدیریت+هتل)

## معرفی

سیستم مدیریت هتل (HMS) یک نرم‌افزار جامع برای مدیریت هتل‌ها و اقامتگاه‌هاست که با استفاده از Django و Django REST Framework توسعه یافته است. این سیستم امکان مدیریت رزروها، اتاق‌ها، مهمانان، پرداخت‌ها و گزارش‌گیری را فراهم می‌کند.

## ویژگی‌های اصلی

- **مدیریت اتاق‌ها**: ثبت، ویرایش و مدیریت انواع اتاق‌ها با امکانات متنوع
- **سیستم رزرواسیون**: رزرو اتاق، مدیریت ورود و خروج مهمانان
- **مدیریت مهمانان**: ثبت اطلاعات مهمانان و سوابق اقامت
- **داشبورد مدیریتی**: نمایش آمار و اطلاعات کلیدی هتل
- **گزارش‌گیری**: امکان تهیه انواع گزارش‌های مدیریتی
- **تقویم رزروها**: نمایش تقویمی رزروها برای مدیریت بهتر
- **API کامل**: دسترسی به تمام قابلیت‌ها از طریق REST API
- **مستندات Swagger**: مستندات کامل API با استفاده از Swagger

## فناوری‌های استفاده شده

- **Django**: فریم‌ورک وب پایتون
- **Django REST Framework**: ساخت REST API
- **Swagger (drf-yasg)**: مستندسازی API
- **SQLite/PostgreSQL**: پایگاه داده
- **AuthToken**: احراز هویت با استفاده از توکن

## ساختار پروژه

پروژه از اپلیکیشن‌های زیر تشکیل شده است:

- **accounts**: مدیریت کاربران و احراز هویت
- **api**: مدیریت API و نقاط پایانی
- **bookings**: مدیریت رزروها و وضعیت آنها
- **guests**: مدیریت اطلاعات مهمانان
- **rooms**: مدیریت اتاق‌ها و انواع آنها
- **payments**: سیستم مدیریت پرداخت‌ها
- **reports**: سیستم گزارش‌گیری
- **services**: خدمات اضافی هتل
- **settings**: تنظیمات سیستم
- **staff**: مدیریت کارکنان هتل

## نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.8+
- pip

### مراحل نصب

1. **دریافت کد منبع**:
   ```bash
   git clone https://github.com/yourusername/hotel-hms.git
   cd hotel-hms
   ```

2. **ایجاد محیط مجازی**:
   ```bash
   python -m venv venv
   # در ویندوز
   venv\Scripts\activate
   # در لینوکس/مک
   source venv/bin/activate
   ```

3. **نصب وابستگی‌ها**:
   ```bash
   pip install -r requirements.txt
   ```

4. **اجرای مایگریشن‌ها**:
   ```bash
   python manage.py migrate
   ```

5. **ایجاد کاربر مدیر**:
   ```bash
   python manage.py createsuperuser
   ```

6. **اجرای سرور توسعه**:
   ```bash
   python manage.py runserver
   ```

7. **تولید داده‌های آزمایشی (اختیاری)**:
   ```bash
   python manage.py shell < fake_data.py
   ```

## استفاده از API

### مستندات API

مستندات کامل API در آدرس‌های زیر در دسترس است:

- **Swagger UI**: `http://127.0.0.1:8000/swagger/`
- **ReDoc**: `http://127.0.0.1:8000/redoc/`

### نمونه درخواست‌ها

#### احراز هویت و دریافت توکن

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login/" \
     -H "Content-Type: application/json" \
     -d '{"email": "style.npr@gmail.com", "password": "toor"}'
```

#### دریافت لیست اتاق‌ها

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/rooms/" \
     -H "Authorization: Token YOUR_TOKEN_HERE"
```

#### ایجاد رزرو جدید

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/bookings/" \
     -H "Authorization: Token YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{
       "room": "101",
       "check_in": "2023-08-15",
       "check_out": "2023-08-20",
       "primary_guest": {
         "national_id": "1234567890",
         "first_name": "علی",
         "last_name": "محمدی",
         "phone": "09123456789"
       }
     }'
```

## نقاط پایانی API

### احراز هویت

- `POST /api/v1/auth/register/`: ثبت نام کاربر جدید
- `POST /api/v1/auth/login/`: ورود کاربر و دریافت توکن
- `POST /api/v1/auth/logout/`: خروج کاربر
- `GET/PUT /api/v1/auth/profile/`: مشاهده و ویرایش پروفایل کاربری

### داشبورد

- `GET /api/v1/dashboard/stats/`: آمار و اطلاعات داشبورد

### مدیریت اتاق‌ها

- `GET /api/v1/rooms/`: فهرست تمام اتاق‌ها
- `POST /api/v1/rooms/`: ایجاد اتاق جدید
- `GET /api/v1/rooms/{number}/`: جزئیات یک اتاق
- `PUT /api/v1/rooms/{number}/`: ویرایش اتاق
- `DELETE /api/v1/rooms/{number}/`: حذف اتاق
- `GET /api/v1/rooms/available/`: یافتن اتاق‌های خالی در بازه زمانی مشخص

### انواع اتاق

- `GET /api/v1/room-types/`: فهرست انواع اتاق
- `POST /api/v1/room-types/`: ایجاد نوع اتاق جدید
- `GET /api/v1/room-types/{id}/`: جزئیات یک نوع اتاق
- `PUT /api/v1/room-types/{id}/`: ویرایش نوع اتاق
- `DELETE /api/v1/room-types/{id}/`: حذف نوع اتاق

### امکانات

- `GET /api/v1/amenities/`: فهرست امکانات
- `POST /api/v1/amenities/`: ایجاد امکان جدید
- `GET /api/v1/amenities/{id}/`: جزئیات یک امکان
- `PUT /api/v1/amenities/{id}/`: ویرایش امکان
- `DELETE /api/v1/amenities/{id}/`: حذف امکان

### رزروها

- `GET /api/v1/bookings/`: فهرست رزروها
- `POST /api/v1/bookings/`: ایجاد رزرو جدید
- `GET /api/v1/bookings/{id}/`: جزئیات یک رزرو
- `PUT /api/v1/bookings/{id}/`: ویرایش رزرو
- `DELETE /api/v1/bookings/{id}/`: حذف رزرو
- `GET /api/v1/bookings/calendar/events/`: رویدادهای تقویم
- `POST /api/v1/bookings/{id}/soft-delete/`: انتقال رزرو به سطل زباله
- `POST /api/v1/bookings/{id}/restore/`: بازیابی رزرو از سطل زباله

### مهمانان

- `GET /api/v1/guests/`: فهرست مهمانان
- `POST /api/v1/guests/`: ایجاد مهمان جدید
- `GET /api/v1/guests/{id}/`: جزئیات یک مهمان
- `PUT /api/v1/guests/{id}/`: ویرایش مهمان
- `DELETE /api/v1/guests/{id}/`: حذف مهمان

### گزارش‌ها

- `GET /api/v1/reports/`: فهرست گزارش‌های موجود
- `GET /api/v1/reports/occupancy/`: آمار اشغال هتل
- `GET /api/v1/reports/bookings/`: آمار رزروها
- `GET /api/v1/reports/guests/`: آمار مهمانان
- `GET /api/v1/reports/staff/`: آمار فعالیت کارکنان

### تنظیمات

- `GET /api/v1/settings/`: فهرست تنظیمات
- `GET /api/v1/settings/1/`: دریافت تنظیمات هتل
- `PUT /api/v1/settings/1/`: به‌روزرسانی تنظیمات هتل

## مدل‌های داده

### مدل کاربر (CustomUser)

- نام کاربری، ایمیل، نام و نام خانوادگی
- شماره تماس و سطح دسترسی

### مدل اتاق (Room)

- شماره اتاق، طبقه، ظرفیت
- وضعیت (خالی، رزرو شده، اشغال شده، در حال تعمیر)
- قیمت، نوع اتاق، امکانات

### مدل نوع اتاق (RoomType)

- نام، توضیحات، قیمت پایه
- حداکثر ظرفیت، متراژ
- امکانات پیش‌فرض

### مدل امکانات (Amenity)

- نام، آیکون، توضیحات
- دسته‌بندی، قابلیت هزینه اضافی

### مدل رزرو (Booking)

- شماره رزرو، اتاق، تاریخ ورود و خروج
- وضعیت (رزرو شده، تأیید شده، ورود، خروج، لغو شده)
- مهمان اصلی، کارمند مسئول
- تعداد بزرگسالان و کودکان
- اطلاعات قیمت و پرداخت

### مدل مهمان (Guest)

- کد ملی، نام و نام خانوادگی
- جنسیت، شماره تماس، ایمیل
- آدرس، تاریخ تولد، ملیت

## توسعه‌دهندگان

- [سینا نقی پور](https://github.com/sina-naghipour)

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای اطلاعات بیشتر به فایل LICENSE مراجعه کنید.

</div>