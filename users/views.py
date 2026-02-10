from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_student = True
            user.save()
            login(request, user)

            # Create JetWallet on signup + welcome bonus
            from gamification.models import JetWallet
            wallet, created = JetWallet.objects.get_or_create(user=user)
            if created:
                wallet.credit(50, "Bônus de Boas-Vindas! 🎉")

            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def index(request):
    from courses.models import Course
    from subscriptions.models import Plan
    courses = Course.objects.all()[:6]
    plans = Plan.objects.filter(is_active=True)[:3]
    
    # Stats for social proof
    total_students = User.objects.filter(is_student=True).count()
    total_courses = Course.objects.count()
    
    return render(request, 'index.html', {
        'courses': courses,
        'plans': plans,
        'total_students': total_students,
        'total_courses': total_courses,
    })


@login_required
def dashboard(request):
    from learning.models import Enrollment, Progress, Certificate
    from assessments.models import Exam
    from django.utils import timezone
    from courses.models import Content

    # Enrollments
    enrollments = request.user.enrollments.select_related('course').all()

    # Real progress calculation
    enrollment_data = []
    for enrollment in enrollments:
        total_contents = Content.objects.filter(module__course=enrollment.course).count()
        completed_contents = Progress.objects.filter(
            student=request.user,
            content__module__course=enrollment.course
        ).count()
        progress = int((completed_contents / total_contents * 100) if total_contents > 0 else 0)
        enrollment_data.append({
            'enrollment': enrollment,
            'progress': progress,
            'completed': completed_contents,
            'total': total_contents,
        })

    # Certificates
    certificates = Certificate.objects.filter(student=request.user)

    # Upcoming Exams
    upcoming_exams = []
    if hasattr(request.user, 'enrolled_classes'):
        user_classes = request.user.enrolled_classes.all()
        upcoming_exams = Exam.objects.filter(
            class_session__in=user_classes,
            is_published=True,
            scheduled_at__gte=timezone.now()
        ).order_by('scheduled_at')[:5]

    return render(request, 'dashboard.html', {
        'enrollments': enrollments,
        'enrollment_data': enrollment_data,
        'certificates': certificates,
        'upcoming_exams': upcoming_exams,
    })
