from django.db import models
from django.conf import settings
from courses.models import Course

class PageView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    url = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class CourseEngagement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    views = models.IntegerField(default=0)
    enrollments_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['course', 'date']
