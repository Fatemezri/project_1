# comments/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Comment, Notification
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Comment, Notification

User = get_user_model()

@receiver(post_save, sender=Comment)
def create_moderator_report_notification(sender, instance, **kwargs):
    if instance.moderator_report and 'moderator_report' in kwargs.get('update_fields', []):
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            Notification.objects.create(
                recipient=superuser,
                sender=instance.user,
                notification_type='moderator_report',
                message=f"ناظر {instance.user.username} گزارشی برای نظر کاربر {instance.user.username} ارسال کرد.",
                related_comment=instance
            )