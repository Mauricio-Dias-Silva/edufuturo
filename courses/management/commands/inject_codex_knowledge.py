
import os
import chromadb
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from courses.models import Course, Module, Content, Quiz, Question, Choice

class Command(BaseCommand):
    help = 'INJECTOR: Lê a memória do Codex-IA e popula o EduFuturo.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧠 INICIANDO PONTE NEURAL (Codex -> EduFuturo)...'))

        # 1. Conectar à Memória do Codex (Caminho Absoluto)
        CODEX_MEMORY_PATH = r"c:\Users\Mauricio\Desktop\codex-IA\.codex_memory"
        
        if not os.path.exists(CODEX_MEMORY_PATH):
            self.stdout.write(self.style.ERROR(f'❌ Memória não encontrada em: {CODEX_MEMORY_PATH}'))
            return

        try:
            client = chromadb.PersistentClient(path=CODEX_MEMORY_PATH)
            collection = client.get_collection("project_codebase")
            self.stdout.write(self.style.SUCCESS('✅ Conexão com Memória Vetorial estabelecida.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao abrir banco vetorial: {e}'))
            return

        # 2. Garantir Usuário "Professor AI"
        User = get_user_model()
        professor, created = User.objects.get_or_create(
            username='CodexAI',
            defaults={'email': 'ai@edufuturo.com', 'is_staff': True}
        )
        if created:
            professor.set_password('codex123')
            professor.save()
            self.stdout.write(self.style.SUCCESS('👤 Professor IA criado.'))

        # 3. Mapear Tópicos da BNCC (Isso filtra o que vamos importar)
        # O script de treino usou o domínio "EDUCACAO_BNCC"
        domain_query = "EDUCACAO_BNCC"
        
        # Como o Chroma não tem um "select * where domain=", vamos fazer uma busca semântica ampla
        # Ou iterar se possível. Para MVP, vamos criar Cursos fixos e buscar conteúdo.
        
        STRUCTURE = {
            "Matemática": ["Álgebra", "Geometria", "Estatística"],
            "Ciências": ["Química Orgânica", "Física Mecânica", "Biologia Celular"],
            "Humanas": ["História do Brasil", "Geografia Física", "Filosofia"],
            "Linguagens": ["Gramática", "Literatura", "Redação"]
        }

        for area, temas in STRUCTURE.items():
            # Criar Curso
            course, created = Course.objects.get_or_create(
                title=f"{area} (BNCC Completa)",
                instructor=professor,
                defaults={'overview': f"Curso completo de {area} gerado por Inteligência Artificial baseado na BNCC."}
            )
            if created:
                self.stdout.write(f'   🎓 Curso Criado: {area}')
            
            for i, tema in enumerate(temas):
                # Criar Módulo
                module, created = Module.objects.get_or_create(
                    course=course,
                    title=tema,
                    defaults={'order': i, 'description': f"Módulo focado em {tema}."}
                )
                
                # Buscar Conteúdo na Memória do Codex
                self.stdout.write(f'      🔍 Buscando conhecimento sobre "{tema}"...')
                
                # Query no Chroma
                results = collection.query(
                    query_texts=[f"Explicação detalhada sobre {tema}"],
                    n_results=3,
                    where={"domain": "EDUCACAO_BNCC"} 
                )
                
                fragments = results['documents'][0] if results['documents'] else []
                
                if fragments:
                    combined_text = "\n\n".join(fragments)
                    
                    # Criar Conteúdo (Aula)
                    content, c_created = Content.objects.get_or_create(
                        module=module,
                        title=f"Aula Magna: {tema}",
                        defaults={
                            'text': combined_text,
                            'order': 0,
                            'video_url': "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Placeholder
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f'      ✅ Aula Gerada: {tema} ({len(combined_text)} chars)'))
                    
                    # Bônus: Criar Quiz Simples
                    quiz, _ = Quiz.objects.get_or_create(module=module, title=f"Quiz de {tema}")
                    if quiz.questions.count() == 0:
                        q = Question.objects.create(quiz=quiz, text=f"Qual o principal conceito de {tema}?")
                        Choice.objects.create(question=q, text="Conceito A (Correto)", is_correct=True)
                        Choice.objects.create(question=q, text="Conceito B (Errado)", is_correct=False)
                        self.stdout.write(f'      ❓ Quiz gerado.')

                else:
                    self.stdout.write(self.style.WARNING(f'      ⚠️ Nenhum conhecimento encontrado para {tema}. (O script de treino ainda está rodando?)'))

        self.stdout.write(self.style.SUCCESS('🚀 PONTE NEURAL CONCLUÍDA. O EduFuturo agora tem cérebro.'))
