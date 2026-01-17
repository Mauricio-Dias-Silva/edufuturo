from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Course
from learning.models import Enrollment

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('dashboard')

@login_required
def lesson_detail(request, slug, content_id):
    from .models import Content
    content = get_object_or_404(Content, id=content_id)
    
    # Check enrollment (simplified)
    # if not Enrollment.objects.filter(user=request.user, course=content.module.course).exists(): ...
    
    youtube_id = None
    if content.video_url:
        import re
        # Basic Regex for YouTube ID
        regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(regex, content.video_url)
        if match:
            youtube_id = match.group(1)

    return render(request, 'courses/lesson.html', {'content': content, 'youtube_id': youtube_id})
