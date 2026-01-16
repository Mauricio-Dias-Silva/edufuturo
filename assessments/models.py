from django.db import models
from django.conf import settings
from academic.models import Discipline, ClassSession

class QuestionBank(models.Model):
    """
    Pool of questions linked to a Discipline (reusable across semesters).
    """
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')], default='MEDIUM')
    
    def __str__(self):
        return f"[{self.discipline.code}] {self.text[:50]}..."

class Exam(models.Model):
    """
    An assessment event (Prova).
    """
    class_session = models.ForeignKey(ClassSession, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=200)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=120)
    weight = models.DecimalField(max_digits=4, decimal_places=2, help_text="Weight in final grade (0.0 to 10.0)")
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.class_session}"

class Submission(models.Model):
    """
    Student's answer sheet for an exam.
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['exam', 'student']

class GradeBook(models.Model):
    """
    Official final grade for a student in a class.
    """
    class_session = models.ForeignKey(ClassSession, related_name='grades', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    final_grade = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    attendance_percentage = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=[('APPROVED', 'Aprovado'), ('FAILED', 'Reprovado')], default='FAILED')
    
    class Meta:
        unique_together = ['class_session', 'student']
