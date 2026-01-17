from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.exam_list, name='exam_list'),
    path('take/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('grade/<int:submission_id>/', views.view_grade, name='view_grade'),
    
    # Teacher Routes
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/results/<int:exam_id>/', views.exam_results, name='exam_results'),
    path('teacher/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
]
