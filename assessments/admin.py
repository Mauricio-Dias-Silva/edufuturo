from django.contrib import admin
from .models import (
    QuestionBank, QuestionOption, 
    Exam, ExamQuestion, 
    Submission, StudentAnswer, 
    GradeBook
)

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 3

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ['discipline', 'question_type', 'difficulty', 'text_preview']
    list_filter = ['discipline', 'question_type', 'difficulty']
    search_fields = ['text']
    inlines = [QuestionOptionInline]
    
    def text_preview(self, obj):
        return obj.text[:50]

class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 1
    autocomplete_fields = ['question']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'class_session', 'scheduled_at', 'is_published', 'total_points']
    list_filter = ['class_session__term', 'is_published']
    search_fields = ['title', 'class_session__discipline__name']
    inlines = [ExamQuestionInline]
    
    def total_points(self, obj):
        # Calculate total points based on questions
        return sum(q.points for q in obj.examquestion_set.all())

class StudentAnswerInline(admin.StackedInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ['is_correct', 'points_awarded']
    can_delete = False

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'grade', 'submitted_at']
    list_filter = ['exam__class_session', 'exam']
    search_fields = ['student__username', 'student__email']
    inlines = [StudentAnswerInline]

@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_session', 'final_grade', 'status']
    list_filter = ['class_session__term', 'status']
    search_fields = ['student__username']
