from django.urls import path
from settings.views import General, Payment, Email

app_name = 'settings'
urlpatterns = [
    path('general/', General.as_view(), name='general'),
    path('payment/', Payment.as_view(), name='payment'),
    path('email/', Email.as_view(), name='email'),

]
