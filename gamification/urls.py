from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('my-wallet/', views.my_wallet, name='my_wallet'),
    path('marketplace/', views.marketplace, name='marketplace'),
]
