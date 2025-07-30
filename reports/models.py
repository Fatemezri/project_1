from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_reports')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen_by_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.title
