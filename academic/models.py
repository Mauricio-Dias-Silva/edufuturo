from django.db import models
from django.conf import settings

class AcademicTerm(models.Model):
    """
    Represents a semester or academic year (e.g., '2026.1').
    """
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Discipline(models.Model):
    """
    A subject taught at the university (e.g., 'Calculus I', 'Data Structures').
    It is independent of the semester.
    """
    code = models.CharField(max_length=10, unique=True, help_text="Ex: MAT101")
    name = models.CharField(max_length=100)
    description = models.TextField()
    credits = models.IntegerField(default=4)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassSession(models.Model):
    """
    A specific instance of a Discipline taught in a Term (Turma).
    """
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, related_name='classes')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, related_name='classes')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        limit_choices_to={'is_instructor': True},
        related_name='teaching_classes'
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='enrolled_classes',
        limit_choices_to={'is_student': True},
        blank=True
    )
    capacity = models.IntegerField(default=50)
    
    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        unique_together = ['discipline', 'term', 'instructor']

    def __str__(self):
        return f"{self.discipline.code} ({self.term}) - Prof. {self.instructor}"
