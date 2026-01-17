from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll'),
    path('<slug:slug>/learn/<int:content_id>/', views.lesson_detail, name='lesson'),
]
