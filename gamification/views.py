from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import JetWallet, Badge

@login_required
def my_wallet(request):
    """
    Exibe a carteira de JetCredits do usuário.
    Se não existir, cria uma (lazy creation).
    """
    wallet, created = JetWallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()[:10] # Últimas 10 transações
    
    # Badges ganhas
    my_badges = request.user.badges.all()

    context = {
        'wallet': wallet,
        'transactions': transactions,
        'badges': my_badges,
        'conversion_rate_brl': wallet.balance / 100 # Simulação: 100 Credits = R$ 1,00
    }
    return render(request, 'gamification/wallet.html', context)

@login_required
def marketplace(request):
    """
    Loja de Recompensas (Spending the JetCredits).
    """
    wallet, _ = JetWallet.objects.get_or_create(user=request.user)
    
    # Mock de Itens da Loja (Futuramente isso viria de um Model 'Reward')
    rewards = [
        {
            'id': 1,
            'title': 'Certificado de Conclusão Oficial',
            'description': 'Certificado com selo EduFuturo para imprimir.',
            'price': 100,
            'icon': 'bi-award',
            'color': 'primary'
        },
        {
            'id': 2,
            'title': 'Mentoria 1:1 (30 min)',
            'description': 'Sessão exclusiva com um especialista da área.',
            'price': 500,
            'icon': 'bi-people',
            'color': 'success'
        },
        {
            'id': 3,
            'title': 'Desconto em Livros (20%)',
            'description': 'Cupom de desconto na Amazon para livros técnicos.',
            'price': 50,
            'icon': 'bi-book',
            'color': 'info'
        },
         {
            'id': 4,
            'title': 'Destaque no Perfil',
            'description': 'Seu perfil no topo da lista de alunos por 1 semana.',
            'price': 200,
            'icon': 'bi-star',
            'color': 'warning'
        }
    ]

    message = None

    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))
        # Lógica simples de compra (Mock)
        # Encontra o item pelo ID (na lista mockada)
        item = next((r for r in rewards if r['id'] == item_id), None)
        
        if item:
            if wallet.debit(item['price'], f"Compra: {item['title']}"):
                message = {'type': 'success', 'text': f"Compra realizada! Você adquiriu '{item['title']}'."}
            else:
                message = {'type': 'danger', 'text': f"Saldo insuficiente para '{item['title']}'."}

    context = {
        'wallet': wallet,
        'rewards': rewards,
        'message': message
    }
    return render(request, 'gamification/marketplace.html', context)
