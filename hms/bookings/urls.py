from django.urls import path
from bookings.views import ListBookings, DetailBookings, CreateBookings, CalendarBookings

app_name = 'bookings'
urlpatterns = [
    path('list/', ListBookings.as_view(), name='list'),
    path('detail/', DetailBookings.as_view(), name='detail'),
    path('create/', CreateBookings.as_view(), name='create'),
    path('calendar/', CalendarBookings.as_view(), name='calendar'),
]
