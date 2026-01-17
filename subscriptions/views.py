from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Plan, Subscription
import mercadopago

@login_required
def subscribe(request, plan_slug):
    plan = get_object_or_404(Plan, slug=plan_slug)
    
    # 1. Integrate with MercadoPago (Pseudo-code until token provided)
    # mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    # preference_data = {
    #     "items": [{"title": plan.name, "quantity": 1, "unit_price": float(plan.price)}],
    #     "back_urls": {"success": "http://localhost:8000/subscriptions/success/"}
    # }
    # preference_response = mp.preference().create(preference_data)
    # checkout_url = preference_response["response"]["init_point"]
    
    # For now, simplistic flow: Create Subscription PENDING -> Redirect to Mock Payment
    sub = Subscription.objects.create(user=request.user, plan=plan, status='PENDING')
    
    # In real world, redirect to checkout_url
    # return redirect(checkout_url)
    
    # Simulation: Auto-approve for demo
    sub.status = 'ACTIVE'
    sub.save()
    
    return render(request, 'subscriptions/success.html', {'subscription': sub})

def plans(request):
    plans = Plan.objects.filter(is_active=True)
    return render(request, 'subscriptions/plans.html', {'plans': plans})
