from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from bookings.models import Booking
from rooms.models import Room
from guests.models import Guest

User = get_user_model()

class AccountType(models.Model):
    """نوع حساب - تعریف می‌کند که این تراکنش از کدوم کارت بانکی، نقد، یا سامانه دیگه بوده"""
    name = models.CharField(max_length=100, verbose_name="نام نوع حساب")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="شماره حساب/کارت")
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="نام بانک")
    
    ACCOUNT_CATEGORIES = [
        ('bank_card', 'کارت بانکی'),
        ('cash', 'نقدی'),
        ('online_gateway', 'درگاه آنلاین'),
        ('pos', 'دستگاه کارت‌خوان'),
        ('bank_transfer', 'حواله بانکی'),
        ('check', 'چک'),
        ('other', 'سایر'),
    ]
    
    category = models.CharField(max_length=20, choices=ACCOUNT_CATEGORIES, verbose_name="دسته‌بندی")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    # اطلاعات اضافی برای درگاه‌های آنلاین
    gateway_config = models.JSONField(blank=True, null=True, verbose_name="تنظیمات درگاه")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "نوع حساب"
        verbose_name_plural = "انواع حساب"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"


class TransactionType(models.Model):
    """نوع تراکنش - تعریف می‌کند که این تراکنش درآمدی هست یا مخارج"""
    name = models.CharField(max_length=100, verbose_name="نام نوع تراکنش")
    code = models.CharField(max_length=20, unique=True, verbose_name="کد")
    
    TRANSACTION_NATURE = [
        ('income', 'درآمد'),
        ('expense', 'مخارج'),
        ('transfer', 'انتقال'),
    ]
    
    nature = models.CharField(max_length=10, choices=TRANSACTION_NATURE, verbose_name="ماهیت تراکنش")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    
    # برای دسته‌بندی بهتر
    parent_type = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="نوع والد")
    
    # تنظیمات حسابداری
    default_account_debit = models.CharField(max_length=20, blank=True, verbose_name="حساب بدهکار پیش‌فرض")
    default_account_credit = models.CharField(max_length=20, blank=True, verbose_name="حساب بستانکار پیش‌فرض")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "نوع تراکنش"
        verbose_name_plural = "انواع تراکنش"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_nature_display()})"


class Transaction(models.Model):
    """جدول اصلی تراکنشات"""
    # شناسه‌ها
    transaction_id = models.CharField(max_length=50, unique=True, verbose_name="شناسه تراکنش")
    
    # ارتباط با منابع مختلف (Source ID که شما گفتید)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, verbose_name="رزرو")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True, verbose_name="مهمان")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, verbose_name="اتاق")
    
    # اطلاعات اصلی تراکنش
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, verbose_name="نوع تراکنش")
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, verbose_name="نوع حساب")
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="مبلغ")
    description = models.TextField(verbose_name="شرح تراکنش")
    
    # تاریخ و زمان
    transaction_date = models.DateTimeField(verbose_name="تاریخ تراکنش")
    
    # اطلاعات مرجع
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="شماره مرجع")
    external_reference = models.CharField(max_length=100, blank=True, verbose_name="مرجع خارجی")
    
    # اطلاعات درگاه پرداخت (اگر آنلاین باشد)
    gateway_transaction_id = models.CharField(max_length=100, blank=True, verbose_name="شناسه تراکنش درگاه")
    gateway_response = models.JSONField(blank=True, null=True, verbose_name="پاسخ درگاه")
    
    # وضعیت تراکنش
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشتی'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    
    # اطلاعات کاربری
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="ایجاد شده توسط")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transactions', verbose_name="تایید شده توسط")
    
    # اطلاعات لغو/برگشت
    is_reversed = models.BooleanField(default=False, verbose_name="برگشت خورده")
    reversed_transaction = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تراکنش برگشتی")
    reversal_reason = models.TextField(blank=True, verbose_name="دلیل برگشت")
    reversed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ برگشت")
    reversed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reversed_transactions', verbose_name="برگشت داده شده توسط")
    
    # فیلدهای زمانی
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنشات"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['booking']),
            models.Index(fields=['guest']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['account_type']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type.name} - {self.amount:,} تومان"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """تولید شناسه یکتا برای تراکنش"""
        import uuid
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        return f"TXN{date_str}{str(uuid.uuid4())[:8].upper()}"
    
    @property
    def is_income(self):
        """آیا این تراکنش درآمدی است؟"""
        return self.transaction_type.nature == 'income'
    
    @property
    def is_expense(self):
        """آیا این تراکنش مخارج است؟"""
        return self.transaction_type.nature == 'expense'
    
    def reverse_transaction(self, user, reason=""):
        """برگشت تراکنش"""
        if self.is_reversed:
            raise ValueError("این تراکنش قبلاً برگشت خورده است")
        
        from django.utils import timezone
        
        # ایجاد تراکنش برگشتی
        reversed_txn = Transaction.objects.create(
            booking=self.booking,
            guest=self.guest,
            room=self.room,
            transaction_type=self.transaction_type,
            account_type=self.account_type,
            amount=self.amount,
            description=f"برگشت تراکنش {self.transaction_id} - {reason}",
            transaction_date=timezone.now(),
            reference_number=f"REV-{self.transaction_id}",
            status='completed',
            created_by=user,
            reversed_transaction=self
        )
        
        # به‌روزرسانی تراکنش اصلی
        self.is_reversed = True
        self.reversed_at = timezone.now()
        self.reversed_by = user
        self.reversal_reason = reason
        self.save()
        
        return reversed_txn


class TransactionAttachment(models.Model):
    """پیوست‌های تراکنش (فیش، رسید، تصاویر و...)"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='attachments', verbose_name="تراکنش")
    file = models.FileField(upload_to='transaction_attachments/', verbose_name="فایل")
    file_type = models.CharField(max_length=50, verbose_name="نوع فایل")
    description = models.CharField(max_length=255, blank=True, verbose_name="توضیحات")
    
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="آپلود شده توسط")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "پیوست تراکنش"
        verbose_name_plural = "پیوست‌های تراکنش"
    
    def __str__(self):
        return f"پیوست {self.transaction.transaction_id}"


class DailyReport(models.Model):
    """گزارش روزانه تراکنشات"""
    date = models.DateField(unique=True, verbose_name="تاریخ")
    
    # خلاصه درآمدها
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="کل درآمد")
    cash_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="درآمد نقدی")
    card_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="درآمد کارتی")
    online_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="درآمد آنلاین")
    
    # خلاصه مخارج
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="کل مخارج")
    cash_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="مخارج نقدی")
    card_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'), verbose_name="مخارج کارتی")
    
    # تعداد تراکنشات
    income_transactions_count = models.IntegerField(default=0, verbose_name="تعداد تراکنشات درآمدی")
    expense_transactions_count = models.IntegerField(default=0, verbose_name="تعداد تراکنشات مخارج")
    
    # وضعیت گزارش
    is_finalized = models.BooleanField(default=False, verbose_name="نهایی شده")
    finalized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="نهایی شده توسط")
    finalized_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ نهایی شدن")
    
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "گزارش روزانه"
        verbose_name_plural = "گزارش‌های روزانه"
        ordering = ['-date']
    
    def __str__(self):
        return f"گزارش {self.date}"
    
    @property
    def net_income(self):
        """سود خالص روز"""
        return self.total_income - self.total_expenses


class AccountingSettings(models.Model):
    """تنظیمات سیستم حسابداری"""
    
    # تنظیمات عمومی
    fiscal_year_start = models.DateField(verbose_name="شروع سال مالی")
    default_currency = models.CharField(max_length=10, default='IRR', verbose_name="ارز پیش‌فرض")
    
    # تنظیمات گزارش‌گیری
    auto_generate_daily_reports = models.BooleanField(default=True, verbose_name="تولید خودکار گزارش روزانه")
    require_transaction_approval = models.BooleanField(default=False, verbose_name="نیاز به تایید تراکنش")
    
    # تنظیمات درگاه پرداخت
    default_gateway_config = models.JSONField(blank=True, null=True, verbose_name="تنظیمات پیش‌فرض درگاه")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "تنظیمات حسابداری"
        verbose_name_plural = "تنظیمات حسابداری"
    
    def __str__(self):
        return f"تنظیمات حسابداری - سال مالی {self.fiscal_year_start.year}"