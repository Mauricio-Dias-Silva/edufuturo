from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import User

# Extends standard UserCreationForm to support custom User model
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Default to student role
            user.is_student = True 
            user.save()
            login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    # Import locally to avoid circular imports if any, though likely safe
    from courses.models import Course
    courses = Course.objects.all()[:3]
    return render(request, 'index.html', {'courses': courses})

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Fetch user enrollments (mock logic since we don't have full enrollment logic connected yet)
    # properly we would do: enrollments = request.user.enrollments.all()
    # For now, to demonstrate, empty or basic query
    enrollments = [] 
    if hasattr(request.user, 'enrollments'):
        enrollments = request.user.enrollments.select_related('course').all()
    
    return render(request, 'dashboard.html', {'enrollments': enrollments})
