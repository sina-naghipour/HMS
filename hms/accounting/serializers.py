from rest_framework import serializers
from .models import AccountType, TransactionType, Transaction, TransactionAttachment, DailyReport, AccountingSettings
from bookings.models import Booking
from guests.models import Guest
from rooms.models import Room


class AccountTypeSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = AccountType
        fields = '__all__'


class TransactionTypeSerializer(serializers.ModelSerializer):
    nature_display = serializers.CharField(source='get_nature_display', read_only=True)
    parent_type_name = serializers.CharField(source='parent_type.name', read_only=True)
    
    class Meta:
        model = TransactionType
        fields = '__all__'


class TransactionAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_size = serializers.SerializerMethodField()
    
    class Meta:
        model = TransactionAttachment
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'uploaded_at']
    
    def get_file_size(self, obj):
        if obj.file:
            return obj.file.size
        return 0


class TransactionSerializer(serializers.ModelSerializer):
    # فیلدهای مرتبط
    transaction_type_name = serializers.CharField(source='transaction_type.name', read_only=True)
    transaction_type_nature = serializers.CharField(source='transaction_type.nature', read_only=True)
    account_type_name = serializers.CharField(source='account_type.name', read_only=True)
    account_type_category = serializers.CharField(source='account_type.category', read_only=True)
    
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    guest_name = serializers.SerializerMethodField()
    room_number = serializers.CharField(source='room.number', read_only=True)
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    reversed_by_name = serializers.CharField(source='reversed_by.get_full_name', read_only=True)
    
    # پیوست‌ها
    attachments = TransactionAttachmentSerializer(many=True, read_only=True)
    
    # فیلدهای محاسباتی
    is_income = serializers.ReadOnlyField()
    is_expense = serializers.ReadOnlyField()
    
    # وضعیت نمایشی
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['transaction_id', 'created_at', 'updated_at', 'is_reversed', 'reversed_at']
    
    def get_guest_name(self, obj):
        if obj.guest:
            return f"{obj.guest.first_name} {obj.guest.last_name}"
        return None
    
    def validate(self, data):
        """اعتبارسنجی داده‌های تراکنش"""
        # بررسی اینکه حداقل یکی از منابع (booking, guest, room) مشخص باشد
        if not any([data.get('booking'), data.get('guest'), data.get('room')]):
            raise serializers.ValidationError("حداقل یکی از فیلدهای رزرو، مهمان یا اتاق باید مشخص شود")
        
        return data


class TransactionCreateSerializer(serializers.ModelSerializer):
    """سریالایزر مخصوص ایجاد تراکنش"""
    
    class Meta:
        model = Transaction
        fields = [
            'booking', 'guest', 'room', 'transaction_type', 'account_type',
            'amount', 'description', 'transaction_date', 'reference_number',
            'external_reference', 'gateway_transaction_id'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class DailyReportSerializer(serializers.ModelSerializer):
    net_income = serializers.ReadOnlyField()
    finalized_by_name = serializers.CharField(source='finalized_by.get_full_name', read_only=True)
    
    class Meta:
        model = DailyReport
        fields = '__all__'


class AccountingSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingSettings
        fields = '__all__'


# سریالایزرهای آماری
class TransactionSummarySerializer(serializers.Serializer):
    """خلاصه آماری تراکنشات"""
    date = serializers.DateField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    transactions_count = serializers.IntegerField()


class AccountTypeReportSerializer(serializers.Serializer):
    """گزارش بر اساس نوع حساب"""
    account_type = serializers.CharField()
    account_category = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transactions_count = serializers.IntegerField()


class TransactionTypeReportSerializer(serializers.Serializer):
    """گزارش بر اساس نوع تراکنش"""
    transaction_type = serializers.CharField()
    nature = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transactions_count = serializers.IntegerField()