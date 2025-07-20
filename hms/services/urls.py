from django.urls import path
from services.views import ListServices, DetailServices

app_name = 'services'
urlpatterns = [
    path('list/', ListServices.as_view(), name='list'),
    path('detail/', DetailServices.as_view(), name='detail'),
]
