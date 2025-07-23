from django.urls import path
from .views import BookingListView, BookingDetailView, BookingCreateView, BookingUpdateView, BookingCalendarView

app_name = 'bookings'

urlpatterns = [
    path('list/', BookingListView.as_view(), name='list'),
    path('create/', BookingCreateView.as_view(), name='create'),
    path('detail/<int:pk>/', BookingDetailView.as_view(), name='detail'),
    path('edit/<int:pk>/', BookingUpdateView.as_view(), name='edit'),
    path('calendar/', BookingCalendarView.as_view(), name='calendar'),
]
