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
    updated_at = models.DateTimeField(auto_now=True)

    def credit(self, amount, description="Crédito"):
        self.balance += amount
        self.save()
        JetTransaction.objects.create(wallet=self, amount=amount, transaction_type='CREDIT', description=description)

    def debit(self, amount, description="Resgate"):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            JetTransaction.objects.create(wallet=self, amount=amount, transaction_type='DEBIT', description=description)
            return True
        return False

    def __str__(self):
        return f"{self.user}: {self.balance} JetCredits"

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
