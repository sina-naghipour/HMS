from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    DashboardStatsView, RoomViewSet, RoomTypeViewSet, AmenityViewSet,
    BookingViewSet, BookingCalendarEventsView, GuestViewSet,
    available_rooms, soft_delete_booking, restore_booking
)
from reports.views import ReportsViewSet
from settings.views import SettingsViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'room-types', RoomTypeViewSet)
router.register(r'amenities', AmenityViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'reports', ReportsViewSet, basename='reports')
router.register(r'settings', SettingsViewSet, basename='settings')

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),

    # Dashboard endpoints
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),

    # Calendar endpoints
    path('bookings/calendar/events/', BookingCalendarEventsView.as_view(), name='calendar_events'),

    # Utility endpoints
    path('rooms/available/', available_rooms, name='available_rooms'),
    path('bookings/<int:pk>/soft-delete/', soft_delete_booking, name='soft_delete_booking'),
    path('bookings/<int:pk>/restore/', restore_booking, name='restore_booking'),

    path('', include(router.urls)),
]