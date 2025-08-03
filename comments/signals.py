# comments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Comment, Notification

User = get_user_model()

@receiver(post_save, sender=Comment)
def create_moderator_report_notification(sender, instance, created, update_fields, **kwargs):
    """
    This signal is triggered after a Comment object is saved.
    It creates a notification for the superuser if a moderator_report has been updated.
    """
    # Check if a new instance was created or if a specific field was updated.
    # 'update_fields' is a set, so check for its existence and for the specific field.
    if update_fields and 'moderator_report' in update_fields:
        print(f"Moderator report updated for comment ID {instance.id}. Creating notification...")
        try:
            # Find the first superuser
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                Notification.objects.create(
                    recipient=superuser,
                    sender=instance.user, # The user who wrote the original comment
                    notification_type='moderator_report',
                    message=f"ناظر {instance.user.username} گزارشی برای نظر کاربر {instance.user.username} ارسال کرد.",
                    related_comment=instance
                )
                print("Notification created successfully.")
            else:
                print("No superuser found to send notification.")
        except Exception as e:
            print(f"Error creating notification: {e}")