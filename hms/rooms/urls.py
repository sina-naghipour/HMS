from django.urls import path
from rooms.views import (
    ListRooms, DetailRooms, CreateRooms,
    ListTypes, EditRoomView, DeleteRoomView,
    RoomTypeDetailView, RoomTypeDeleteView, RoomTypeCreateView, RoomTypeEditView, RoomTypeListView

)

app_name = 'rooms'
urlpatterns = [
    path('list/', ListRooms.as_view(), name='list'),
    path('detail/<int:number>/', DetailRooms.as_view(), name='detail'),
    path('create/', CreateRooms.as_view(), name='create'),
    path('edit/<int:number>/', EditRoomView.as_view(), name='edit'),
    path('delete/<int:number>/', DeleteRoomView.as_view(), name='delete'),

    path('types/list/', RoomTypeListView.as_view(), name='types_list'),
    path('types/detail/<int:pk>/', RoomTypeDetailView.as_view(), name='types_detail'),
    path('types/delete/<int:pk>/', RoomTypeDeleteView.as_view(), name='types_delete'),
    path('types/create/', RoomTypeCreateView.as_view(), name='types_create'),
    path('types/edit/<int:pk>/', RoomTypeEditView.as_view(), name='types_edit'),

]
