from django.urls import path
from rooms.views import ListRooms, DetailRooms, CreateRooms, DetailTypes, ListTypes

app_name = 'rooms'
urlpatterns = [
    path('list/', ListRooms.as_view(), name='list'),
    path('detail/', DetailRooms.as_view(), name='detail'),
    path('create/', CreateRooms.as_view(), name='create'),
    path('types/list/', ListTypes.as_view(), name='types_list'),
    path('types/detail/', DetailTypes.as_view(), name='types_detail'),
]
