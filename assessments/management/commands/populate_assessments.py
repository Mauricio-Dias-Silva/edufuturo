from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from academic.models import AcademicTerm, Discipline, ClassSession
from assessments.models import QuestionBank, QuestionOption, Exam, ExamQuestion
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample assessment data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # 1. Ensure Users (Teacher & Student)
        student, _ = User.objects.get_or_create(username='aluno_teste', email='aluno@teste.com')
        if not student.check_password('123'):
            student.set_password('123')
            student.is_student = True
            student.save()

        teacher, _ = User.objects.get_or_create(username='prof_teste', email='prof@teste.com')
        if not teacher.check_password('123'):
            teacher.set_password('123')
            teacher.is_instructor = True
            teacher.save()

        # 2. Academic Structure
        term, _ = AcademicTerm.objects.get_or_create(
            name='2026.1',
            defaults={
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=180),
                'is_active': True
            }
        )

        discipline, _ = Discipline.objects.get_or_create(
            code='MAT101',
            defaults={'name': 'Matemática Básica', 'description': 'Fundamentos de Álgebra e Aritmética'}
        )

        class_session, created = ClassSession.objects.get_or_create(
            discipline=discipline,
            term=term,
            instructor=teacher
        )
        class_session.students.add(student)
        self.stdout.write(f'Class {class_session} ready with student {student.username}')

        # 3. Question Bank (Multiple Choice, True/False, Fill Blank, Essay)
        
        # MC Question
        q1, _ = QuestionBank.objects.get_or_create(
            discipline=discipline,
            text='Quanto é 2 + 2?',
            defaults={'question_type': 'MULTIPLE_CHOICE', 'difficulty': 'EASY'}
        )
        if q1.options.count() == 0:
            QuestionOption.objects.create(question=q1, text='3', is_correct=False)
            QuestionOption.objects.create(question=q1, text='4', is_correct=True)
            QuestionOption.objects.create(question=q1, text='5', is_correct=False)

        # True/False
        q2, _ = QuestionBank.objects.get_or_create(
            discipline=discipline,
            text='O número 17 é primo.',
            defaults={'question_type': 'TRUE_FALSE', 'difficulty': 'MEDIUM'}
        )
        if q2.options.count() == 0:
            QuestionOption.objects.create(question=q2, text='Verdadeiro', is_correct=True)
            QuestionOption.objects.create(question=q2, text='Falso', is_correct=False)

        # Fill The Blank
        q3, _ = QuestionBank.objects.get_or_create(
            discipline=discipline,
            text='A capital da França é _____.',
            defaults={'question_type': 'FILL_THE_BLANK', 'difficulty': 'EASY'}
        )
        if q3.options.count() == 0: # Storing the correct answer as an option
            QuestionOption.objects.create(question=q3, text='paris', is_correct=True)

        # Essay
        q4, _ = QuestionBank.objects.get_or_create(
            discipline=discipline,
            text='Explique o Teorema de Pitágoras.',
            defaults={'question_type': 'ESSAY', 'difficulty': 'HARD'}
        )

        all_questions = [q1, q2, q3, q4]

        # 4. Create Exams
        
        # Exam 1: Future (Upcoming)
        exam_future, _ = Exam.objects.get_or_create(
            title='Prova A1 - Álgebra',
            class_session=class_session,
            defaults={
                'scheduled_at': timezone.now() + timedelta(days=2),
                'duration_minutes': 90,
                'weight': 3.0,
                'is_published': True
            }
        )
        # Add questions
        if exam_future.questions.count() == 0:
            for i, q in enumerate(all_questions):
                ExamQuestion.objects.create(exam=exam_future, question=q, order=i+1, points=2.5)

        # Exam 2: Today (Available Now)
        exam_now, _ = Exam.objects.get_or_create(
            title='Quiz Relâmpago',
            class_session=class_session,
            defaults={
                'scheduled_at': timezone.now() + timedelta(hours=1),
                'duration_minutes': 30,
                'weight': 1.0,
                'is_published': True
            }
        )
         # Add questions (subset)
        if exam_now.questions.count() == 0:
            ExamQuestion.objects.create(exam=exam_now, question=q1, order=1, points=5.0)
            ExamQuestion.objects.create(exam=exam_now, question=q2, order=2, points=5.0)

        self.stdout.write(self.style.SUCCESS(f'Successfully populated data! Login as {student.username} / 123'))
