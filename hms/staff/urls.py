from django.urls import path
from staff.views import ListStaff, DetailStaff

app_name = 'staff'

urlpatterns = [
    path('list/', ListStaff.as_view(), name='list'),
    path('detail/', DetailStaff.as_view(), name='detail'),
]
