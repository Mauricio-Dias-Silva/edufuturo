from django.db import models
from django.conf import settings
from academic.models import Discipline, ClassSession

class QuestionBank(models.Model):
    """
    Pool of questions linked to a Discipline (reusable across semesters).
    """
    TYPE_CHOICES = [
        ('MULTIPLE_CHOICE', 'Múltipla Escolha'),
        ('ESSAY', 'Dissertativa'),
        ('TRUE_FALSE', 'Verdadeiro/Falso'),
        ('FILL_THE_BLANK', 'Preencher Lacuna'),
    ]

    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='MULTIPLE_CHOICE')
    difficulty = models.CharField(max_length=20, choices=[('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard')], default='MEDIUM')
    
    def __str__(self):
        return f"[{self.discipline.code}] {self.text[:50]}..."

class QuestionOption(models.Model):
    """
    Options for multiple choice questions.
    """
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

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
    
    questions = models.ManyToManyField(QuestionBank, through='ExamQuestion', related_name='exams')

    def __str__(self):
        return f"{self.title} - {self.class_session}"

class ExamQuestion(models.Model):
    """
    Link between Exam and Question, allowing custom points per question in each exam.
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    points = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['exam', 'question']

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

class StudentAnswer(models.Model):
    """
    Individual answer for a question in a submission.
    """
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(QuestionOption, on_delete=models.SET_NULL, null=True, blank=True)
    text_answer = models.TextField(blank=True, null=True) # For essay questions
    is_correct = models.BooleanField(null=True, blank=True) # Calulated automatically or manual grading
    points_awarded = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)

    class Meta:
        unique_together = ['submission', 'question']

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
