import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edufuturo.settings')
django.setup()

from gamification.models import Reward

rewards = [
    {
        'title': 'Certificado Digital Oficial',
        'price': 100,
        'category': 'certificate',
        'icon': 'bi-patch-check-fill',
        'color': 'primary',
        'description': 'Certificado verificado com QR Code, válido para horas complementares e currículo.'
    },
    {
        'title': 'Mentoria de Carreira (30min)',
        'price': 500,
        'category': 'mentorship',
        'icon': 'bi-people-fill',
        'color': 'success',
        'description': 'Sessão individual com um especialista de mercado para revisar seu currículo.'
    },
    {
        'title': 'Kit EduFuturo (Camiseta + Caneca)',
        'price': 1200,
        'category': 'merchandise',
        'icon': 'bi-gift-fill',
        'color': 'danger',
        'description': 'Receba em casa nosso kit exclusivo para alunos Diamante. Frete grátis.'
    },
    {
        'title': 'Desconto de 20% em Cursos',
        'price': 50,
        'category': 'discount',
        'icon': 'bi-tag-fill',
        'color': 'warning',
        'description': 'Cupom de desconto válido para a compra de qualquer curso pago da plataforma.'
    },
    {
        'title': 'Destaque no Perfil',
        'price': 200,
        'category': 'feature',
        'icon': 'bi-star-fill',
        'color': 'info',
        'description': 'Seu perfil aparecerá em destaque na lista de alunos e para recrutadores por 7 dias.'
    }
]

print("Populating rewards...")
for r in rewards:
    obj, created = Reward.objects.get_or_create(
        title=r['title'],
        defaults={
            'price': r['price'],
            'category': r['category'],
            'icon': r['icon'],
            'color': r['color'],
            'description': r['description'],
            'stock': -1 if r['category'] in ['certificate', 'discount', 'feature'] else 50
        }
    )
    if created:
        print(f"Created: {r['title']}")
    else:
        print(f"Already exists: {r['title']}")

print("Done!")
