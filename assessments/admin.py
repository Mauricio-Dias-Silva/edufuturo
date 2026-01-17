from django.contrib import admin
from .models import QuestionBank, Exam, Submission, GradeBook

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['discipline', 'difficulty', 'text_preview']
    list_filter = ['discipline', 'difficulty']
    
    def text_preview(self, obj):
        return obj.text[:50]

class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['submitted_at']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_session', 'scheduled_at', 'is_published']
    list_filter = ['class_session__term', 'is_published']
    inlines = [SubmissionInline]

@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_session', 'final_grade', 'status']
    list_filter = ['class_session__term', 'status']
