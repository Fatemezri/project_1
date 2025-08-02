from django.db import models
from django.conf import settings

# Get the custom user model defined in your `user` app
User = settings.AUTH_USER_MODEL

class Comment(models.Model):
    """
    Model for storing user comments.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    moderator_report = models.TextField(blank=True, null=True,
                                        help_text="Report from the moderator to the superuser.")

    class Meta:
        ordering = ['-created_at']
        verbose_name = ("نظر")
        verbose_name_plural = ("نظرات")
        permissions = (
            ("can_moderate_comments", ("اجازه‌ی بررسی نظرات")),
        )

    def __str__(self):
        return f"Comment by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"

class Notification(models.Model):
    """
    Model to store internal notifications for admins.
    """
    NOTIFICATION_CHOICES = (
        ('new_comment', 'New Comment'),
        ('comment_approved', 'Comment Approved'),
        ('moderator_report', 'Moderator Report'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.get_notification_type_display()}"
