import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)  # لاگر مخصوص این فایل

class Command(BaseCommand):
    help = 'Send evening greeting email to all users'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        users = User.objects.filter(is_active=True, email__isnull=False)
        success_count = 0
        fail_count = 0

        for user in users:
            try:
                send_mail(
                    subject="Good Evening!",
                    message=f"Good evening, {user.get_full_name() or user.username}!",
                    from_email="noreply@example.com",  # با ایمیل واقعی جایگزین کن
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                logger.info(f"Email sent to {user.email}")
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to send email to {user.email}: {e}")
                fail_count += 1

        msg = f"Evening emails completed. Success: {success_count}, Failed: {fail_count}"
        self.stdout.write(self.style.SUCCESS(msg))
        logger.info(msg)
