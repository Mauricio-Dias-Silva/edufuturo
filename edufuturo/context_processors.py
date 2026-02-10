"""Global context processors — inject wallet data into every template."""


def wallet_context(request):
    """Inject JetCredits wallet data into navbar and all templates."""
    if request.user.is_authenticated:
        from gamification.models import JetWallet
        wallet, _ = JetWallet.objects.get_or_create(user=request.user)
        return {
            'user_wallet': wallet,
            'jet_balance': wallet.balance,
            'jet_level': wallet.level,
        }
    return {
        'user_wallet': None,
        'jet_balance': 0,
        'jet_level': '',
    }
