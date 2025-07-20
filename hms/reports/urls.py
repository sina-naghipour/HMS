from django.urls import path
from reports.views import Occupancy, Revenue, Custom

app_name = 'reports'

urlpatterns = [
    path('occupancy/', Occupancy.as_view(), name='occupancy'),
    path('revenue/', Revenue.as_view(), name='revenue'),
    path('custom/', Custom.as_view(), name='custom'),
]
