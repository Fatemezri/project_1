from django.db import models
from django.conf import settings

class Message(models.Model):
    """مدل برای پیام‌های داخلی بین مدیران و سوپریوزرها."""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'پیام از {self.sender.username} به {self.recipient.username}'
