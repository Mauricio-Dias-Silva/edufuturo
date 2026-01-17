from django.contrib import admin
from .models import AcademicTerm, Discipline, ClassSession

@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits']
    search_fields = ['code', 'name']

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ['discipline', 'term', 'instructor', 'capacity']
    list_filter = ['term', 'instructor']
    autocomplete_fields = ['discipline', 'term', 'instructor']
