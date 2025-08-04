import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .signals import good_evening_email_sent_signal, good_evening_email_failed_signal

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


@shared_task
def send_good_evening_email_task():
    """
    ارسال ایمیل 'عصر بخیر' به تمامی کاربران فعال دارای ایمیل.
    """
    logger.info("Starting 'send_good_evening_email_task'...")

    User = get_user_model()
    # فقط کاربران فعال و دارای ایمیل رو انتخاب کنید
    users = User.objects.filter(is_active=True).exclude(email__isnull=True).exclude(email__exact='')

    if not users:
        logger.warning("No active users with email found to send good evening message. Task finished.")
        return

    recipient_list = [user.email for user in users]
    subject = "عصر بخیر از ما!"
    message = "عصر شما بخیر! امیدواریم روز خوبی داشته باشید."

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"✅ Successfully sent good evening email to {len(recipient_list)} users at {timezone.now()}")
        # ارسال سیگنال مربوط به ارسال موفقیت آمیز
        good_evening_email_sent_signal.send(sender=None, count=len(recipient_list))
    except Exception as e:
        logger.error(f"❌ Error sending good evening email: {e}", exc_info=True)
        # ارسال سیگنال مربوط به خطای ارسال
        good_evening_email_failed_signal.send(sender=None, error=str(e))
