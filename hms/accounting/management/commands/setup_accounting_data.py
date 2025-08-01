from django.core.management.base import BaseCommand
from accounting.models import AccountType, TransactionType, AccountingSettings
from django.utils import timezone

class Command(BaseCommand):
    help = 'راه‌اندازی داده‌های اولیه سیستم حسابداری'

    def handle(self, *args, **options):
        # ایجاد انواع حساب
        account_types = [
            {
                'name': 'صندوق نقد',
                'category': 'cash',
                'description': 'پول نقد موجود در صندوق هتل'
            },
            {
                'name': 'کارت بانک ملی',
                'account_number': '1234567890123456',
                'bank_name': 'بانک ملی ایران',
                'category': 'bank_card',
                'description': 'کارت بانک ملی هتل'
            },
            {
                'name': 'دستگاه کارت‌خوان',
                'category': 'pos',
                'description': 'دستگاه کارت‌خوان پذیرش هتل'
            },
            {
                'name': 'درگاه زرین‌پال',
                'category': 'online_gateway',
                'description': 'درگاه پرداخت آنلاین زرین‌پال',
                'gateway_config': {'merchant_id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
            },
            {
                'name': 'حواله بانکی',
                'category': 'bank_transfer',
                'description': 'واریزی مستقیم به حساب هتل'
            },
        ]
        
        for account_data in account_types:
            account, created = AccountType.objects.get_or_create(
                name=account_data['name'],
                defaults=account_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'نوع حساب ایجاد شد: {account.name}'))
        
        # ایجاد انواع تراکنش
        transaction_types = [
            # درآمدها
            {
                'name': 'پرداخت رزرو اتاق',
                'code': 'BOOKING_PAYMENT',
                'nature': 'income',
                'description': 'پرداخت توسط مهمان برای رزرو اتاق'
            },
            {
                'name': 'پرداخت خدمات اضافی',
                'code': 'SERVICE_PAYMENT',
                'nature': 'income',
                'description': 'پرداخت خدمات اضافی مانند اسپا، رستوران و...'
            },
            {
                'name': 'پرداخت نقدی',
                'code': 'CASH_PAYMENT',
                'nature': 'income',
                'description': 'پرداخت نقدی مهمان'
            },
            {
                'name': 'پرداخت کارتی',
                'code': 'CARD_PAYMENT',
                'nature': 'income',
                'description': 'پرداخت با کارت بانکی'
            },
            
            # مخارج
            {
                'name': 'تعمیرات و نگهداری',
                'code': 'MAINTENANCE',
                'nature': 'expense',
                'description': 'هزینه‌های تعمیرات اتاق‌ها و تجهیزات'
            },
            {
                'name': 'خرید مواد شوینده',
                'code': 'CLEANING_SUPPLIES',
                'nature': 'expense',
                'description': 'خرید مواد شوینده و نظافت'
            },
            {
                'name': 'پرداخت حقوق',
                'code': 'SALARY_PAYMENT',
                'nature': 'expense',
                'description': 'پرداخت حقوق کارمندان'
            },
            {
                'name': 'قبض آب و برق',
                'code': 'UTILITIES',
                'nature': 'expense',
                'description': 'پرداخت قبوض آب، برق، گاز'
            },
            {
                'name': 'خرید تجهیزات',
                'code': 'EQUIPMENT_PURCHASE',
                'nature': 'expense',
                'description': 'خرید تجهیزات جدید برای هتل'
            },
            {
                'name': 'تبلیغات و بازاریابی',
                'code': 'MARKETING',
                'nature': 'expense',
                'description': 'هزینه‌های تبلیغات و بازاریابی'
            },
            
            # انتقالات
            {
                'name': 'انتقال بین حساب‌ها',
                'code': 'TRANSFER',
                'nature': 'transfer',
                'description': 'انتقال پول بین حساب‌های مختلف'
            },
        ]
        
        for txn_data in transaction_types:
            txn_type, created = TransactionType.objects.get_or_create(
                code=txn_data['code'],
                defaults=txn_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'نوع تراکنش ایجاد شد: {txn_type.name}'))
        
        # ایجاد تنظیمات حسابداری
        settings, created = AccountingSettings.objects.get_or_create(
            id=1,
            defaults={
                'fiscal_year_start': timezone.now().date().replace(month=1, day=1),
                'default_currency': 'IRR',
                'auto_generate_daily_reports': True,
                'require_transaction_approval': False,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('تنظیمات حسابداری ایجاد شد'))
        
        self.stdout.write(self.style.SUCCESS('راه‌اندازی سیستم حسابداری تکمیل شد!'))