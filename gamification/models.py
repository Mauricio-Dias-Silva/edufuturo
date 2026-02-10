from django.db import models
from django.conf import settings

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    points_value = models.IntegerField(default=10)
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='badges', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']

class JetWallet(models.Model):
    """
    Carteira de Fidelidade do Usuário (JetCredits).
    Funciona como o 'Km de Vantagens': o aluno acumula e troca por benefícios.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='wallet', on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo em JetCredits")
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Ganho")
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Gasto")
    level = models.CharField(max_length=20, default='Iniciante')
    updated_at = models.DateTimeField(auto_now=True)

    def credit(self, amount, description="Crédito"):
        self.balance += amount
        self.total_earned += amount
        self._update_level()
        self.save()
        JetTransaction.objects.create(wallet=self, amount=amount, transaction_type='CREDIT', description=description)

    def debit(self, amount, description="Resgate"):
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            self.save()
            JetTransaction.objects.create(wallet=self, amount=amount, transaction_type='DEBIT', description=description)
            return True
        return False

    def _update_level(self):
        if self.total_earned >= 5000:
            self.level = 'Diamante'
        elif self.total_earned >= 2000:
            self.level = 'Ouro'
        elif self.total_earned >= 500:
            self.level = 'Prata'
        elif self.total_earned >= 100:
            self.level = 'Bronze'
        else:
            self.level = 'Iniciante'

    def __str__(self):
        return f"{self.user}: {self.balance} JetCredits ({self.level})"

class JetTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Crédito (Ganho)'),
        ('DEBIT', 'Débito (Uso/Resgate)'),
    ]
    wallet = models.ForeignKey(JetWallet, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.created_at})"


class Reward(models.Model):
    """Recompensa resgatável com JetCredits."""
    CATEGORY_CHOICES = [
        ('certificate', 'Certificado'),
        ('mentorship', 'Mentoria'),
        ('discount', 'Desconto'),
        ('feature', 'Funcionalidade Premium'),
        ('merchandise', 'Merchandise'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço (JetCredits)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='feature')
    icon = models.CharField(max_length=30, default='bi-gift', help_text="Bootstrap Icon class")
    color = models.CharField(max_length=20, default='primary', help_text="Bootstrap color")
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField(default=-1, help_text="-1 = ilimitado")
    image = models.ImageField(upload_to='rewards/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.title} — {self.price} JC"

    @property
    def available(self):
        return self.is_active and (self.stock == -1 or self.stock > 0)


class RewardRedemption(models.Model):
    """Registro de resgate de recompensa."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='redemptions')
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} resgatou {self.reward.title}"
