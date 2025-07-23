from django.urls import path
from .views import BookingListView, BookingDetailView, BookingCreateView, BookingDeleteView, BookingUpdateView, BookingCalendarView, BookingCalendarEventsView

app_name = 'bookings'

urlpatterns = [
    path('list/', BookingListView.as_view(), name='list'),
    path('create/', BookingCreateView.as_view(), name='create'),
    path('detail/<int:pk>/', BookingDetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', BookingDeleteView.as_view(), name='delete'),
    path('edit/<int:pk>/', BookingUpdateView.as_view(), name='edit'),
    path('calendar/', BookingCalendarView.as_view(), name='calendar'),
        path('calendar/events/', BookingCalendarEventsView.as_view(), name='calendar_events'),

]
