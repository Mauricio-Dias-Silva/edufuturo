import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class AICourseGenerator:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured in settings.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_course_structure(self, topic):
        """
        Generates a course structure (title, overview, modules, lessons) for a given topic.
        Returns a Python dictionary.
        """
        prompt = f"""
        Act as an expert curriculum designer.
        Create a comprehensive course structure for the topic: "{topic}".
        
        The output must be valid JSON with the following schema:
        {{
            "title": "Course Title",
            "overview": "Brief and engaging course overview (max 300 chars)",
            "modules": [
                {{
                    "title": "Module 1 Title",
                    "lessons": [
                        {{
                            "title": "Lesson 1 Title",
                            "description": "Brief lesson description"
                        }},
                        ...
                    ]
                }},
                ...
            ]
        }}
        Create at least 3 modules and 3-5 lessons per module.
        Ensure the content is educational, structured, and progressive using Portuguese.
        Return ONLY valid JSON. Do not include markdown formatting like ```json.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Cleanup potential markdown formatting
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error generating course structure: {e}")
            return None

    def generate_lesson_content(self, course_title, module_title, lesson_title):
        """
        Generates the educational content for a specific lesson in Markdown format.
        """
        prompt = f"""
        Act as an expert professor for the course "{course_title}".
        Write a detailed, engaging, and educational lesson content for:
        Module: "{module_title}"
        Lesson: "{lesson_title}"
        
        The content should be in Markdown format.
        Include:
        - Introduction
        - Key Concepts (with examples)
        - Practical Application
        - Summary
        
        Keep the tone professional yet accessible.
        Use Python code blocks if relevant to the topic.
        Language: Portuguese.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating lesson content: {e}")
            return "Conteúdo indisponível no momento. Tente novamente mais tarde."

    def generate_quiz(self, module_title, content_context):
        """
        Generates a quiz (Question + Choices + Correct Answer) based on the content.
        Returns a list of dictionaries.
        """
        prompt = f"""
        Create a quiz with 3 multiple-choice questions based on the following module content:
        Module: "{module_title}"
        Content Context: "{content_context[:1000]}..."
        
        Output valid JSON schema:
        [
            {{
                "question": "Question text?",
                "choices": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                "correct_answer": "A) Option 1",
                "explanation": "Why this is correct."
            }}
        ]
        Return ONLY valid JSON.
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return []
