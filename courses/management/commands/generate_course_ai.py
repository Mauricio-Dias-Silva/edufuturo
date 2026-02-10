from django.core.management.base import BaseCommand
from courses.services.ai_generator import AICourseGenerator
from courses.models import Course, Module, Content
from users.models import User
from django.utils.text import slugify
import time

class Command(BaseCommand):
    help = 'Generates a full course using AI (Gemini)'

    def add_arguments(self, parser):
        parser.add_argument('topic', type=str, help='The topic of the course to generate')
        parser.add_argument('--instructor', type=str, default='ai.bot', help='Username of the instructor')

    def handle(self, *args, **kwargs):
        topic = kwargs['topic']
        instructor_username = kwargs['instructor']

        self.stdout.write(f'🤖 Initializing AI for topic: "{topic}"...')
        
        generator = AICourseGenerator()
        
        # Get or create instructor
        instructor, _ = User.objects.get_or_create(
            username=instructor_username,
            defaults={'first_name': 'AI', 'last_name': 'Instructor', 'is_instructor': True}
        )

        # 1. Generate Structure
        self.stdout.write('   Generating course structure (this may take a moment)...')
        structure = generator.generate_course_structure(topic)
        
        if not structure:
            self.stdout.write(self.style.ERROR('Failed to generate course structure.'))
            return

        # 2. Create Course
        course_title = structure.get('title', f'Curso de {topic}')
        course, created = Course.objects.get_or_create(
            title=course_title,
            defaults={
                'slug': slugify(course_title),
                'overview': structure.get('overview', ''),
                'instructor': instructor
            }
        )
        
        if not created:
            self.stdout.write(self.style.WARNING(f'Course "{course_title}" already exists. updating content...'))

        self.stdout.write(self.style.SUCCESS(f'   Course created: {course_title}'))

        # 3. Create Modules & Lessons
        for mod_idx, mod_data in enumerate(structure.get('modules', []), 1):
            module, _ = Module.objects.get_or_create(
                course=course,
                title=mod_data['title'],
                defaults={'order': mod_idx}
            )
            self.stdout.write(f'   + Module {mod_idx}: {module.title}')

            for lesson_idx, lesson_data in enumerate(mod_data.get('lessons', []), 1):
                lesson_title = lesson_data['title']
                self.stdout.write(f'     - Generating content for: {lesson_title}...')
                
                # Generate Content
                content_text = generator.generate_lesson_content(course_title, module.title, lesson_title)
                
                # Save Content
                Content.objects.get_or_create(
                    module=module,
                    title=lesson_title,
                    defaults={
                        'text': content_text,
                        'order': lesson_idx,
                        'video_url': None  # AI generates text primarily
                    }
                )
                
                # Sleep to avoid rate limits
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS(f'✨ Course generation complete! Check it out at /courses/{course.slug}/'))
