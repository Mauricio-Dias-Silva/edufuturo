from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JetWallet, Badge, Reward, RewardRedemption


@login_required
def my_wallet(request):
    wallet, created = JetWallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()[:15]
    my_badges = request.user.badges.select_related('badge').all()

    # Level progress
    level_thresholds = {
        'Iniciante': (0, 100),
        'Bronze': (100, 500),
        'Prata': (500, 2000),
        'Ouro': (2000, 5000),
        'Diamante': (5000, 99999),
    }
    current_range = level_thresholds.get(wallet.level, (0, 100))
    level_progress = min(100, int(
        (float(wallet.total_earned) - current_range[0]) / max(1, current_range[1] - current_range[0]) * 100
    ))

    context = {
        'wallet': wallet,
        'transactions': transactions,
        'badges': my_badges,
        'level_progress': level_progress,
        'next_level_at': current_range[1],
    }
    return render(request, 'gamification/wallet.html', context)


@login_required
def marketplace(request):
    wallet, _ = JetWallet.objects.get_or_create(user=request.user)
    rewards = Reward.objects.filter(is_active=True)
    message = None

    if request.method == 'POST':
        reward_id = request.POST.get('reward_id')
        try:
            reward = Reward.objects.get(id=reward_id, is_active=True)
            if not reward.available:
                message = {'type': 'warning', 'text': f"'{reward.title}' está esgotado."}
            elif wallet.debit(reward.price, f"Resgate: {reward.title}"):
                RewardRedemption.objects.create(user=request.user, reward=reward)
                if reward.stock > 0:
                    reward.stock -= 1
                    reward.save()
                message = {'type': 'success', 'text': f"Você resgatou '{reward.title}'! 🎉"}
            else:
                message = {'type': 'danger', 'text': f"Saldo insuficiente para '{reward.title}'."}
        except Reward.DoesNotExist:
            message = {'type': 'danger', 'text': 'Recompensa não encontrada.'}

    context = {
        'wallet': wallet,
        'rewards': rewards,
        'message': message,
    }
    return render(request, 'gamification/marketplace.html', context)
