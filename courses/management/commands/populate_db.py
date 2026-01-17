from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from courses.models import Course, Module, Content, Quiz, Question, Choice
from academic.models import AcademicTerm, Discipline, ClassSession
import datetime
import random

class Command(BaseCommand):
    help = 'Populate database with MASSIVE demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating Heavy Demo Data...')

        # 1. Create Superuser (if not exists)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

        # 2. Create 5 Instructors
        instructors = []
        for i in range(1, 6):
            inst, _ = User.objects.get_or_create(username=f'prof.demo{i}', defaults={
                'email': f'prof{i}@edufuturo.com', 
                'first_name': f'Professor {i}',
                'last_name': 'Silva',
                'is_instructor': True
            })
            inst.set_password('123456')
            inst.save()
            instructors.append(inst)
        
        # 3. Create 10 Students
        students = []
        for i in range(1, 11):
            stu, _ = User.objects.get_or_create(username=f'aluno.demo{i}', defaults={
                'email': f'aluno{i}@edufuturo.com',
                'first_name': f'Aluno {i}',
                'last_name': 'Santos',
                'is_student': True
            })
            stu.set_password('123456')
            stu.save()
            students.append(stu)

        # 4. Create 10 Courses (Diverse Topics)
        topics = [
            ('Python para Data Science', 'Domine pandas, numpy e matplotlib.'),
            ('Marketing Digital Avançado', 'Estratégias de SEO e Tráfego Pago.'),
            ('Gastronomia Molecular', 'A ciência por trás da culinária moderna.'),
            ('Finanças Pessoais', 'Como investir e sair das dívidas.'),
            ('Inglês para Negócios', 'Vocabulário corporativo essencial.'),
            ('Desenvolvimento Mobile com Flutter', 'Crie apps para iOS e Android.'),
            ('Liderança Ágil', 'Gestão de times com Scrum e Kanban.'),
            ('Fotografia Profissional', 'Domine a luz e a composição.'),
            ('Direito Constitucional', 'Preparatório para concursos.'),
            ('História da Arte', 'Do Renascimento ao Modernismo.')
        ]

        for i, (title, overview) in enumerate(topics):
            course, _ = Course.objects.get_or_create(
                slug=f'curso-{i}',
                defaults={
                    'title': title,
                    'instructor': random.choice(instructors),
                    'overview': overview
                }
            )
            
            # Create 3 Modules per course
            for m in range(1, 4):
                mod, _ = Module.objects.get_or_create(course=course, title=f'Módulo {m}: Fundamentos', order=m)
                
                # Create Content
                # Using 'Big Buck Bunny' (Open Content) to ensure it plays embedded
                Content.objects.get_or_create(module=mod, title=f'Aula {m}.1 - Introdução', order=1, defaults={'video_url': 'https://www.youtube.com/watch?v=aqz-KE-bpKQ'})
                Content.objects.get_or_create(module=mod, title=f'Aula {m}.2 - Prática', order=2, defaults={'text': 'Conteúdo de leitura...'})

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(instructors)} instructors, {len(students)} students and 10 courses!'))
