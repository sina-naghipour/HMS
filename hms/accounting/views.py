from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Sum, Q, Count
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    AccountType, TransactionType, Transaction, TransactionAttachment, 
    DailyReport, AccountingSettings
)
from .serializers import (
    AccountTypeSerializer, TransactionTypeSerializer, TransactionSerializer,
    TransactionCreateSerializer, TransactionAttachmentSerializer,
    DailyReportSerializer, AccountingSettingsSerializer,
    TransactionSummarySerializer, AccountTypeReportSerializer, TransactionTypeReportSerializer
)


class AccountTypeViewSet(ModelViewSet):
    """مدیریت انواع حساب"""
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="فهرست انواع حساب",
        operation_description="دریافت لیست تمام انواع حساب (کارت بانکی، نقدی، درگاه و...)"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ایجاد نوع حساب",
        operation_description="ایجاد نوع حساب جدید"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="جزئیات نوع حساب",
        operation_description="دریافت جزئیات یک نوع حساب"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش نوع حساب",
        operation_description="ویرایش کامل نوع حساب"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش بخشی نوع حساب",
        operation_description="ویرایش بخشی از نوع حساب"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="حذف نوع حساب",
        operation_description="حذف یک نوع حساب"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس دسته‌بندی
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # فیلتر فعال/غیرفعال
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class TransactionTypeViewSet(ModelViewSet):
    """مدیریت انواع تراکنش"""
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="فهرست انواع تراکنش",
        operation_description="دریافت لیست تمام انواع تراکنش (درآمدی، مخارج، انتقال)"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ایجاد نوع تراکنش",
        operation_description="ایجاد نوع تراکنش جدید"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="جزئیات نوع تراکنش",
        operation_description="دریافت جزئیات یک نوع تراکنش"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش نوع تراکنش",
        operation_description="ویرایش کامل نوع تراکنش"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش بخشی نوع تراکنش",
        operation_description="ویرایش بخشی از نوع تراکنش"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="حذف نوع تراکنش",
        operation_description="حذف یک نوع تراکنش"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس ماهیت (درآمد/مخارج)
        nature = self.request.query_params.get('nature')
        if nature:
            queryset = queryset.filter(nature=nature)
        
        # فیلتر فعال/غیرفعال
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # فیلتر انواع اصلی (بدون والد)
        main_types_only = self.request.query_params.get('main_types_only')
        if main_types_only and main_types_only.lower() == 'true':
            queryset = queryset.filter(parent_type__isnull=True)
        
        return queryset


class TransactionViewSet(ModelViewSet):
    """مدیریت تراکنشات"""
    queryset = Transaction.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    @swagger_auto_schema(
        operation_summary="فهرست تراکنشات",
        operation_description="دریافت لیست تمام تراکنشات با قابلیت فیلتر",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="از تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="تا تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('transaction_type', openapi.IN_QUERY, description="نوع تراکنش", type=openapi.TYPE_INTEGER),
            openapi.Parameter('account_type', openapi.IN_QUERY, description="نوع حساب", type=openapi.TYPE_INTEGER),
            openapi.Parameter('booking', openapi.IN_QUERY, description="شناسه رزرو", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="وضعیت", type=openapi.TYPE_STRING),
            openapi.Parameter('nature', openapi.IN_QUERY, description="ماهیت (income/expense)", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ایجاد تراکنش",
        operation_description="ایجاد تراکنش جدید"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="جزئیات تراکنش",
        operation_description="دریافت جزئیات یک تراکنش"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش تراکنش",
        operation_description="ویرایش کامل تراکنش"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش بخشی تراکنش",
        operation_description="ویرایش بخشی از تراکنش"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="حذف تراکنش",
        operation_description="حذف یک تراکنش"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر تاریخی
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(transaction_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__date__lte=end_date)
        
        # فیلتر نوع تراکنش
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type_id=transaction_type)
        
        # فیلتر نوع حساب
        account_type = self.request.query_params.get('account_type')
        if account_type:
            queryset = queryset.filter(account_type_id=account_type)
        
        # فیلتر رزرو
        booking = self.request.query_params.get('booking')
        if booking:
            queryset = queryset.filter(booking_id=booking)
        
        # فیلتر وضعیت
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # فیلتر ماهیت (درآمد/مخارج)
        nature = self.request.query_params.get('nature')
        if nature:
            queryset = queryset.filter(transaction_type__nature=nature)
        
        # فیلتر تراکنشات برگشتی
        include_reversed = self.request.query_params.get('include_reversed')
        if not include_reversed or include_reversed.lower() != 'true':
            queryset = queryset.filter(is_reversed=False)
        
        return queryset.select_related(
            'transaction_type', 'account_type', 'booking', 'guest', 'room', 'created_by'
        ).prefetch_related('attachments')
    
    @swagger_auto_schema(
        operation_summary="برگشت تراکنش",
        operation_description="برگشت یک تراکنش",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='دلیل برگشت'),
            }
        )
    )
    @action(detail=True, methods=['post'])
    def reverse_transaction(self, request, pk=None):
        """برگشت تراکنش"""
        transaction_obj = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            reversed_txn = transaction_obj.reverse_transaction(request.user, reason)
            serializer = self.get_serializer(reversed_txn)
            return Response({
                'message': 'تراکنش با موفقیت برگشت داده شد',
                'reversed_transaction': serializer.data
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="تایید تراکنش",
        operation_description="تایید یک تراکنش"
    )
    @action(detail=True, methods=['post'])
    def approve_transaction(self, request, pk=None):
        """تایید تراکنش"""
        transaction_obj = self.get_object()
        
        if transaction_obj.status != 'pending':
            return Response({'error': 'فقط تراکنشات در انتظار قابل تایید هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        transaction_obj.status = 'completed'
        transaction_obj.approved_by = request.user
        transaction_obj.save()
        
        serializer = self.get_serializer(transaction_obj)
        return Response({
            'message': 'تراکنش با موفقیت تایید شد',
            'transaction': serializer.data
        })


class DailyReportViewSet(ModelViewSet):
    """مدیریت گزارش‌های روزانه"""
    queryset = DailyReport.objects.all()
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="فهرست گزارش‌های روزانه",
        operation_description="دریافت لیست گزارش‌های روزانه"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ایجاد گزارش روزانه",
        operation_description="ایجاد گزارش روزانه جدید"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="جزئیات گزارش روزانه",
        operation_description="دریافت جزئیات یک گزارش روزانه"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش گزارش روزانه",
        operation_description="ویرایش کامل گزارش روزانه"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="ویرایش بخشی گزارش روزانه",
        operation_description="ویرایش بخشی از گزارش روزانه"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="حذف گزارش روزانه",
        operation_description="حذف یک گزارش روزانه"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="تولید گزارش روزانه",
        operation_description="تولید گزارش روزانه برای تاریخ مشخص",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='تاریخ گزارش'),
            }
        )
    )
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """تولید گزارش روزانه"""
        report_date = request.data.get('date')
        if not report_date:
            report_date = timezone.now().date()
        else:
            report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        # بررسی وجود گزارش
        existing_report = DailyReport.objects.filter(date=report_date).first()
        if existing_report and existing_report.is_finalized:
            return Response({'error': 'گزارش این تاریخ قبلاً نهایی شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # محاسبه آمار
        transactions = Transaction.objects.filter(
            transaction_date__date=report_date,
            status='completed',
            is_reversed=False
        )
        
        # درآمدها
        income_transactions = transactions.filter(transaction_type__nature='income')
        total_income = income_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        cash_income = income_transactions.filter(account_type__category='cash').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        card_income = income_transactions.filter(account_type__category__in=['bank_card', 'pos']).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        online_income = income_transactions.filter(account_type__category='online_gateway').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # مخارج
        expense_transactions = transactions.filter(transaction_type__nature='expense')
        total_expenses = expense_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        cash_expenses = expense_transactions.filter(account_type__category='cash').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        card_expenses = expense_transactions.filter(account_type__category__in=['bank_card', 'pos']).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # ایجاد یا به‌روزرسانی گزارش
        report_data = {
            'date': report_date,
            'total_income': total_income,
            'cash_income': cash_income,
            'card_income': card_income,
            'online_income': online_income,
            'total_expenses': total_expenses,
            'cash_expenses': cash_expenses,
            'card_expenses': card_expenses,
            'income_transactions_count': income_transactions.count(),
            'expense_transactions_count': expense_transactions.count(),
        }
        
        report, created = DailyReport.objects.update_or_create(
            date=report_date,
            defaults=report_data
        )
        
        serializer = self.get_serializer(report)
        return Response({
            'message': 'گزارش با موفقیت تولید شد' if created else 'گزارش به‌روزرسانی شد',
            'report': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def finalize_report(self, request, pk=None):
        """نهایی کردن گزارش"""
        report = self.get_object()
        
        if report.is_finalized:
            return Response({'error': 'این گزارش قبلاً نهایی شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        report.is_finalized = True
        report.finalized_by = request.user
        report.finalized_at = timezone.now()
        report.save()
        
        serializer = self.get_serializer(report)
        return Response({
            'message': 'گزارش با موفقیت نهایی شد',
            'report': serializer.data
        })


# ویوهای گزارش‌گیری
class TransactionSummaryView(APIView):
    """خلاصه آماری تراکنشات"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="خلاصه آماری تراکنشات",
        operation_description="دریافت خلاصه آماری تراکنشات در بازه زمانی",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="از تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="تا تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
            openapi.Parameter('group_by', openapi.IN_QUERY, description="گروه‌بندی (day/month)", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', 'day')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date و end_date الزامی هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        transactions = Transaction.objects.filter(
            transaction_date__date__gte=start_date,
            transaction_date__date__lte=end_date,
            status='completed',
            is_reversed=False
        )
        
        summary = []
        
        if group_by == 'day':
            current_date = start_date
            while current_date <= end_date:
                day_transactions = transactions.filter(transaction_date__date=current_date)
                
                income = day_transactions.filter(transaction_type__nature='income').aggregate(
                    total=Sum('amount'))['total'] or Decimal('0')
                expenses = day_transactions.filter(transaction_type__nature='expense').aggregate(
                    total=Sum('amount'))['total'] or Decimal('0')
                
                summary.append({
                    'date': current_date,
                    'total_income': income,
                    'total_expenses': expenses,
                    'net_income': income - expenses,
                    'transactions_count': day_transactions.count()
                })
                
                current_date += timedelta(days=1)
        
        elif group_by == 'month':
            # گروه‌بندی ماهانه
            from django.db.models import Extract
            monthly_data = transactions.extra(
                select={'month': "DATE_FORMAT(transaction_date, '%%Y-%%m')"}
            ).values('month').annotate(
                total_income=Sum('amount', filter=Q(transaction_type__nature='income')),
                total_expenses=Sum('amount', filter=Q(transaction_type__nature='expense')),
                transactions_count=Count('id')
            ).order_by('month')
            
            for month_data in monthly_data:
                income = month_data['total_income'] or Decimal('0')
                expenses = month_data['total_expenses'] or Decimal('0')
                
                summary.append({
                    'date': f"{month_data['month']}-01",
                    'total_income': income,
                    'total_expenses': expenses,
                    'net_income': income - expenses,
                    'transactions_count': month_data['transactions_count']
                })
        
        serializer = TransactionSummarySerializer(summary, many=True)
        return Response(serializer.data)


class AccountTypeReportView(APIView):
    """گزارش بر اساس نوع حساب"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="گزارش نوع حساب",
        operation_description="گزارش تراکنشات بر اساس نوع حساب",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="از تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="تا تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
        ]
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date و end_date الزامی هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        transactions = Transaction.objects.filter(
            transaction_date__date__gte=start_date,
            transaction_date__date__lte=end_date,
            status='completed',
            is_reversed=False
        ).select_related('account_type')
        
        report_data = transactions.values(
            'account_type__name',
            'account_type__category'
        ).annotate(
            total_amount=Sum('amount'),
            transactions_count=Count('id')
        ).order_by('-total_amount')
        
        result = []
        for item in report_data:
            result.append({
                'account_type': item['account_type__name'],
                'account_category': item['account_type__category'],
                'total_amount': item['total_amount'],
                'transactions_count': item['transactions_count']
            })
        
        serializer = AccountTypeReportSerializer(result, many=True)
        return Response(serializer.data)


class TransactionTypeReportView(APIView):
    """گزارش بر اساس نوع تراکنش"""
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="گزارش نوع تراکنش",
        operation_description="گزارش تراکنشات بر اساس نوع تراکنش",
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="از تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="تا تاریخ", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=True),
        ]
    )
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response({'error': 'start_date و end_date الزامی هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        transactions = Transaction.objects.filter(
            transaction_date__date__gte=start_date,
            transaction_date__date__lte=end_date,
            status='completed',
            is_reversed=False
        ).select_related('transaction_type')
        
        report_data = transactions.values(
            'transaction_type__name',
            'transaction_type__nature'
        ).annotate(
            total_amount=Sum('amount'),
            transactions_count=Count('id')
        ).order_by('-total_amount')
        
        result = []
        for item in report_data:
            result.append({
                'transaction_type': item['transaction_type__name'],
                'nature': item['transaction_type__nature'],
                'total_amount': item['total_amount'],
                'transactions_count': item['transactions_count']
            })
        
        serializer = TransactionTypeReportSerializer(result, many=True)
        return Response(serializer.data)


# توابع کمکی
@swagger_auto_schema(
    method='post',
    operation_summary="ثبت پرداخت رزرو",
    operation_description="ثبت پرداخت مربوط به یک رزرو",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='شناسه رزرو'),
            'account_type_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='شناسه نوع حساب'),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='مبلغ'),
            'reference_number': openapi.Schema(type=openapi.TYPE_STRING, description='شماره مرجع'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='توضیحات'),
        }
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def record_booking_payment(request):
    """ثبت پرداخت رزرو"""
    from bookings.models import Booking
    
    booking_id = request.data.get('booking_id')
    account_type_id = request.data.get('account_type_id')
    amount = request.data.get('amount')
    reference_number = request.data.get('reference_number', '')
    description = request.data.get('description', '')
    
    if not all([booking_id, account_type_id, amount]):
        return Response({'error': 'booking_id, account_type_id و amount الزامی هستند'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
        booking = Booking.objects.get(id=booking_id)
        account_type = AccountType.objects.get(id=account_type_id)
        
        # پیدا کردن نوع تراکنش پرداخت رزرو
        payment_transaction_type = TransactionType.objects.filter(
            code='BOOKING_PAYMENT'
        ).first()
        
        if not payment_transaction_type:
            return Response({'error': 'نوع تراکنش پرداخت رزرو تعریف نشده است'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # ایجاد تراکنش
        transaction_obj = Transaction.objects.create(
            booking=booking,
            guest=booking.primary_guest,
            room=booking.room,
            transaction_type=payment_transaction_type,
            account_type=account_type,
            amount=Decimal(str(amount)),
            description=description or f"پرداخت رزرو {booking.booking_reference}",
            transaction_date=timezone.now(),
            reference_number=reference_number,
            status='completed',
            created_by=request.user
        )
        
        # به‌روزرسانی وضعیت پرداخت رزرو
        booking.advance_payment += Decimal(str(amount))
        if booking.advance_payment >= booking.total_amount:
            booking.payment_status = 'paid'
        else:
            booking.payment_status = 'partial'
        booking.save()
        
        serializer = TransactionSerializer(transaction_obj)
        return Response({
            'message': 'پرداخت با موفقیت ثبت شد',
            'transaction': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    except Booking.DoesNotExist:
        return Response({'error': 'رزرو یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    except AccountType.DoesNotExist:
        return Response({'error': 'نوع حساب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_summary="ثبت هزینه",
    operation_description="ثبت یک هزینه جدید",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'transaction_type_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='شناسه نوع تراکنش'),
            'account_type_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='شناسه نوع حساب'),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='مبلغ'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, description='توضیحات'),
            'reference_number': openapi.Schema(type=openapi.TYPE_STRING, description='شماره مرجع'),
        }
    )
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def record_expense(request):
    """ثبت هزینه"""
    transaction_type_id = request.data.get('transaction_type_id')
    account_type_id = request.data.get('account_type_id')
    amount = request.data.get('amount')
    description = request.data.get('description')
    reference_number = request.data.get('reference_number', '')
    
    if not all([transaction_type_id, account_type_id, amount, description]):
        return Response({'error': 'تمام فیلدهای الزامی باید پر شوند'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
        transaction_type = TransactionType.objects.get(id=transaction_type_id)
        account_type = AccountType.objects.get(id=account_type_id)
        
        # بررسی اینکه نوع تراکنش از نوع مخارج باشد
        if transaction_type.nature != 'expense':
            return Response({'error': 'نوع تراکنش انتخابی باید از نوع مخارج باشد'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # ایجاد تراکنش
        transaction_obj = Transaction.objects.create(
            transaction_type=transaction_type,
            account_type=account_type,
            amount=Decimal(str(amount)),
            description=description,
            transaction_date=timezone.now(),
            reference_number=reference_number,
            status='completed',
            created_by=request.user
        )
        
        serializer = TransactionSerializer(transaction_obj)
        return Response({
            'message': 'هزینه با موفقیت ثبت شد',
            'transaction': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    except TransactionType.DoesNotExist:
        return Response({'error': 'نوع تراکنش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    except AccountType.DoesNotExist:
        return Response({'error': 'نوع حساب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)