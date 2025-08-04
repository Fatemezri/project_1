# D:\PROJECT\MIZAN_GOSTAR\PROJECT\COMMENT\signals.py

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Comment

# دریافت مدل کاربر
User = get_user_model()

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def notify_superusers_on_new_comment(sender, instance, created, **kwargs):
    """
    هنگامی که یک کامنت جدید و تایید نشده ثبت می‌شود، به سوپریوزرها ایمیل ارسال می‌کند.
    """
    if created and not instance.is_approved:
        logger.info(
            f"New comment (ID: {instance.pk}) from user '{instance.user.username}' created. Notifying superusers.")
        subject = f'کامنت جدیدی از طرف {instance.user.username} ثبت شد'
        message = f'یک کامنت جدید از طرف {instance.user.username} ثبت شده و منتظر تایید است.\n\nمحتوا:\n"{instance.content}"'
        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            superuser_emails = [user.email for user in User.objects.filter(is_superuser=True, is_active=True)]
            if superuser_emails:
                logger.info(f"Found {len(superuser_emails)} active superusers. Attempting to send notification email.")
                send_mail(subject, message, from_email, superuser_emails, fail_silently=False)
                logger.info("✅ Notification email sent successfully to superusers.")
            else:
                logger.warning("No active superusers with email found to send notification.")
        except Exception as e:
            logger.error(f"❌ Error sending notification email for new comment (ID: {instance.pk}): {e}", exc_info=True)