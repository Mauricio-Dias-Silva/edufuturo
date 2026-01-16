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

class UserPoints(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='points', on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user}: {self.total_points}"
