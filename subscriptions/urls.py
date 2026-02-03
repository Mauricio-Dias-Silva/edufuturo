from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.plans, name='plans'),
    path('subscribe/<slug:plan_slug>/', views.subscribe, name='subscribe'),
    path('success/', views.success, name='success'),
]
