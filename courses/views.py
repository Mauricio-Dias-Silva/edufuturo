from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Course, Content
from learning.models import Enrollment, Progress


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user, course=self.object
            ).exists()
            # Count completed contents
            total = Content.objects.filter(module__course=self.object).count()
            done = Progress.objects.filter(
                student=self.request.user, content__module__course=self.object
            ).count()
            ctx['progress'] = int((done / total * 100) if total > 0 else 0)
        return ctx


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    
    if created:
        # Award JetCredits for enrolling
        from gamification.models import JetWallet
        wallet, _ = JetWallet.objects.get_or_create(user=request.user)
        wallet.credit(20, f"Matrícula: {course.title}")
    
    return redirect('dashboard')


@login_required
def lesson_detail(request, slug, content_id):
    content = get_object_or_404(Content, id=content_id)
    course = content.module.course

    # Verify enrollment
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        from django.contrib import messages
        messages.warning(request, "Você precisa se matricular primeiro.")
        return redirect('courses:detail', slug=slug)

    youtube_id = content.get_youtube_id()

    # Completion logic (anti-farm: only credit once per content)
    credits_earned = False
    already_completed = Progress.objects.filter(student=request.user, content=content).exists()

    if request.method == 'POST' and 'complete_lesson' in request.POST:
        if not already_completed:
            Progress.objects.create(student=request.user, content=content)

            # Award JetCredits (anti-farm: only once per content)
            from gamification.models import JetWallet
            wallet, _ = JetWallet.objects.get_or_create(user=request.user)
            wallet.credit(10, f"Aula: {content.title}")
            credits_earned = True

            # Check if course is complete
            total = Content.objects.filter(module__course=course).count()
            done = Progress.objects.filter(student=request.user, content__module__course=course).count()
            if done >= total and total > 0:
                # Mark enrollment as completed + bonus
                enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
                if enrollment and not enrollment.completed:
                    enrollment.completed = True
                    enrollment.save()
                    wallet.credit(100, f"Curso Completo: {course.title} 🎓")

    return render(request, 'courses/lesson.html', {
        'content': content,
        'youtube_id': youtube_id,
        'credits_earned': credits_earned,
        'already_completed': already_completed,
    })
