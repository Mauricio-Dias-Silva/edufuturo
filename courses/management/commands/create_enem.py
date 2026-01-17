from django.core.management.base import BaseCommand
from users.models import User
from courses.models import Course, Module, Content
from subscriptions.models import Plan

class Command(BaseCommand):
    help = 'Create ENEM Social Course'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating ENEM Social Course...')

        # 1. Create Social Plan (Free)
        plan, _ = Plan.objects.get_or_create(
            name='Vestibular Social', 
            slug='social', 
            defaults={'price': 0.00, 'description': 'Bolsa 100% para estudantes de rede pública.'}
        )

        # 2. Professor 'Voluntário'
        inst, _ = User.objects.get_or_create(username='prof.voluntario', defaults={'first_name': 'Prof. Solidário', 'is_instructor': True})
        inst.set_password('123456')
        inst.save()

        # 3. Create Course
        course, _ = Course.objects.get_or_create(
            slug='intensivao-enem-2026',
            defaults={
                'title': 'Intensivão ENEM 2026 (Gratuito)',
                'instructor': inst,
                'overview': 'Preparatório completo com aulas ao vivo todas as noites. Matemática, Redação e Ciências.'
            }
        )

        # 4. Modules
        mod_mat, _ = Module.objects.get_or_create(course=course, title='Matemática - A Base', order=1)
        mod_red, _ = Module.objects.get_or_create(course=course, title='Redação Nota 1000', order=2)

        # 5. Live Classes (Mock YouTube Live Links)
        Content.objects.get_or_create(
            module=mod_mat, 
            title='🔴 AULA AO VIVO: Potenciação e Radiciação', 
            order=1, 
            defaults={
                'video_url': 'https://www.youtube.com/watch?v=5rT88f7H6i4', # Example Live
                'is_live': True,
                'text': 'A aula começa às 19:00. <br>Link para tirar dúvidas no chat.'
            }
        )
        
        Content.objects.get_or_create(
            module=mod_red, 
            title='Estrutura da Dissertação', 
            order=1, 
            defaults={'video_url': 'https://www.youtube.com/watch?v=RPgE6aD-kC0'} # Recorded
        )

        self.stdout.write(self.style.SUCCESS('ENEM Course Created!'))
