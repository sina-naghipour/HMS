from django.urls import path
from guests.views import ListGuests, DetailGuests, CreateGuests

app_name = 'guests'

urlpatterns = [
    path('list/', ListGuests.as_view(), name='list'),
    path('detail/<int:pk>/', DetailGuests.as_view(), name='detail'),
]
