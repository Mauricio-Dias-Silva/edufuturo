from django.db import models
from django.conf import settings
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=100) # e.g., 'Pro Mensal', 'Premium Anual'
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 29.90
    duration_days = models.IntegerField(default=30) # 30 for monthly, 365 for yearly
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - R$ {self.price}"

class Subscription(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('ACTIVE', 'Ativo'),
        ('EXPIRED', 'Expirado'),
        ('CANCELED', 'Cancelado'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    mercadopago_id = models.CharField(max_length=100, blank=True, null=True) # External Transaction ID
    
    def save(self, *args, **kwargs):
        if not self.end_date and self.status == 'ACTIVE':
            from datetime import timedelta
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return self.status == 'ACTIVE' and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.status})"
