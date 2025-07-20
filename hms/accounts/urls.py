from django.urls import path
from accounts.views import Dashboard

app_name = 'accounts'
urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
]
