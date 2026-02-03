from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from .models import Plan, Subscription
import mercadopago
import os

@login_required
def subscribe(request, plan_slug):
    plan = get_object_or_404(Plan, slug=plan_slug)
    
    # Check if MercadoPago is enabled via environment variable
    use_mercadopago = os.getenv('ENABLE_MERCADOPAGO', 'False').lower() == 'true'
    mercadopago_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
    
    if use_mercadopago and mercadopago_token:
        # Production Mode: Real MercadoPago Integration
        try:
            mp = mercadopago.SDK(mercadopago_token)
            
            # Build success URL dynamically
            success_url = request.build_absolute_uri('/subscriptions/success/')
            
            preference_data = {
                "items": [{
                    "title": plan.name,
                    "quantity": 1,
                    "unit_price": float(plan.price)
                }],
                "back_urls": {
                    "success": success_url,
                    "failure": request.build_absolute_uri('/subscriptions/plans/'),
                    "pending": success_url
                },
                "auto_return": "approved",
            }
            
            preference_response = mp.preference().create(preference_data)
            checkout_url = preference_response["response"]["init_point"]
            
            # Create subscription as PENDING
            sub = Subscription.objects.create(
                user=request.user,
                plan=plan,
                status='PENDING',
                mercadopago_id=preference_response["response"]["id"]
            )
            
            # Redirect to MercadoPago checkout
            return redirect(checkout_url)
            
        except Exception as e:
            messages.error(request, f'Erro ao processar pagamento: {str(e)}')
            return redirect('subscriptions:plans')
    
    else:
        # Development/Mock Mode: Auto-approve for testing
        sub = Subscription.objects.create(user=request.user, plan=plan, status='PENDING')
        
        # Auto-approve simulation
        sub.status = 'ACTIVE'
        sub.save()
        
        messages.success(request, f'Assinatura {plan.name} ativada com sucesso! (Modo Demo)')
        return render(request, 'subscriptions/success.html', {'subscription': sub})

def plans(request):
    plans = Plan.objects.filter(is_active=True)
    return render(request, 'subscriptions/plans.html', {'plans': plans})

@login_required
def success(request):
    """Display success page after subscription"""
    # Get user's most recent active subscription
    subscription = Subscription.objects.filter(
        user=request.user,
        status='ACTIVE'
    ).order_by('-start_date').first()
    
    if not subscription:
        # Fallback: show any recent subscription
        subscription = Subscription.objects.filter(
            user=request.user
        ).order_by('-start_date').first()
    
    return render(request, 'subscriptions/success.html', {'subscription': subscription})
