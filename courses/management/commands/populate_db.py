from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from courses.models import Course, Module, Content, Quiz, Question, Choice
from academic.models import AcademicTerm, Discipline, ClassSession
import datetime

class Command(BaseCommand):
    help = 'Populate database with demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating Demo Data...')

        # 1. Create Superuser & Instructors
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Admin created (admin/admin123)')

        inst, _ = User.objects.get_or_create(username='prof.silva', defaults={'email': 'silva@edufuturo.com', 'is_instructor': True})
        inst.set_password('123456')
        inst.save()

        student, _ = User.objects.get_or_create(username='aluno.teste', defaults={'email': 'aluno@edufuturo.com', 'is_student': True})
        student.set_password('123456')
        student.save()

        # 2. Academic Data
        term, _ = AcademicTerm.objects.get_or_create(
            name='2026.1', 
            defaults={'start_date': datetime.date(2026, 2, 1), 'end_date': datetime.date(2026, 6, 30), 'is_active': True}
        )

        disc_math, _ = Discipline.objects.get_or_create(code='MAT101', defaults={'name': 'Cálculo I', 'credits': 4})
        disc_prog, _ = Discipline.objects.get_or_create(code='PROG101', defaults={'name': 'Algoritmos e Programação', 'credits': 4})

        ClassSession.objects.get_or_create(discipline=disc_math, term=term, instructor=inst)
        ClassSession.objects.get_or_create(discipline=disc_prog, term=term, instructor=inst)

        # 3. Create a Demo Course (LMS Style)
        course, _ = Course.objects.get_or_create(
            slug='python-fullstack',
            defaults={
                'title': 'Python Fullstack Masterclass',
                'instructor': inst,
                'overview': 'Aprenda Django, DRF e React do zero ao deploy.'
            }
        )

        # Module 1
        mod1, _ = Module.objects.get_or_create(course=course, title='Introdução ao Python', order=1)
        Content.objects.get_or_create(module=mod1, title='Instalando o Python', order=1, defaults={'video_url': 'https://www.youtube.com/watch?v=rfscVS0vtbw'})
        Content.objects.get_or_create(module=mod1, title='Variáveis e Tipos', order=2, defaults={'text': 'Em Python, a tipagem é dinâmica...'})

        # Quiz
        quiz, _ = Quiz.objects.get_or_create(module=mod1, title='Quiz de Fixação')
        q1, _ = Question.objects.get_or_create(quiz=quiz, text='Qual a extensão de arquivos Python?')
        Choice.objects.get_or_create(question=q1, text='.py', is_correct=True)
        Choice.objects.get_or_create(question=q1, text='.java', is_correct=False)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
