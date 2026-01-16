from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('EduFuturo Info', {'fields': ('is_instructor', 'is_student', 'bio', 'avatar')}),
    )
    list_display = ('username', 'email', 'is_instructor', 'is_student')
