from django.contrib import admin
from .models import Course, Module, Content, Quiz, Question, Choice

class ContentInline(admin.TabularInline):
    model = Content
    extra = 1

class QuizInline(admin.StackedInline):
    model = Quiz
    extra = 0

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0
    show_change_link = True  # Allows clicking to edit the module in detail

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'created']
    search_fields = ['title', 'overview']
    list_filter = ['created', 'instructor']
    inlines = [ModuleInline]
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [ContentInline, QuizInline]
    search_fields = ['title', 'course__title']

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'module']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz']
    inlines = [ChoiceInline]
