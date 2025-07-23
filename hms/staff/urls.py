from django.urls import path
from staff.views import ListStaffView, DetailStaffView, CreateStaffView, UpdateStaffView, DeleteStaffView

app_name = 'staff'

urlpatterns = [
    path('list/', ListStaffView.as_view(), name='list'),
    path('detail/<int:pk>/', DetailStaffView.as_view(), name='detail'),
    path('create/', CreateStaffView.as_view(), name='create'),
    path('edit/<int:pk>/', UpdateStaffView.as_view(), name='edit'),
    path('delete/<int:pk>/', DeleteStaffView.as_view(), name='delete'),
]
