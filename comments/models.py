from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    moderator_report = models.TextField(blank=True, null=True)

    class Meta:
        permissions = [
            ("can_moderate_comments", "Can access the moderator admin panel and moderate comments"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('moderator_report', 'گزارش ناظر'),
        ('new_comment', 'نظر جدید'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    related_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} to {self.recipient}"
