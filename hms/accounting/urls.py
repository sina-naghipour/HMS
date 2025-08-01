from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'accounting'

router = DefaultRouter()
router.register(r'account-types', views.AccountTypeViewSet, basename='account-types')
router.register(r'transaction-types', views.TransactionTypeViewSet, basename='transaction-types')
router.register(r'transactions', views.TransactionViewSet, basename='transactions')
router.register(r'daily-reports', views.DailyReportViewSet, basename='daily-reports')

urlpatterns = [
    path('', include(router.urls)),
    
    # گزارش‌ها
    path('reports/summary/', views.TransactionSummaryView.as_view(), name='transaction-summary'),
    path('reports/account-types/', views.AccountTypeReportView.as_view(), name='account-type-report'),
    path('reports/transaction-types/', views.TransactionTypeReportView.as_view(), name='transaction-type-report'),
    
    # توابع کمکی
    path('record-booking-payment/', views.record_booking_payment, name='record-booking-payment'),
    path('record-expense/', views.record_expense, name='record-expense'),
]