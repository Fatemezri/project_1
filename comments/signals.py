# comments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Comment, Report

User = get_user_model()

@receiver(post_save, sender=Comment)
def create_moderator_report(sender, instance, created, update_fields, **kwargs):
    if update_fields and 'moderator_report' in update_fields:
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                Report.objects.create(
                    recipient=superuser,
                    sender=instance.user,
                    report_type='moderator_report',
                    message=f"ناظر {instance.user.username} گزارشی برای نظر کاربر {instance.user.username} ارسال کرد.",
                    related_comment=instance
                )
        except Exception as e:
            print(f"Error creating report: {e}")