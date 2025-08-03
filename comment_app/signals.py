from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Comment

User = get_user_model()


@receiver(post_save, sender=Comment)
def notify_superusers_on_new_comment(sender, instance, created, **kwargs):
    """هنگامی که یک کامنت جدید و تایید نشده ثبت می‌شود، به سوپریوزرها ایمیل ارسال می‌کند."""
    if created and not instance.is_approved:
        subject = f'کامنت جدیدی از طرف {instance.user.username} ثبت شد'
        message = f'یک کامنت جدید از طرف {instance.user.username} ثبت شده و منتظر تایید است.\n\nمحتوا:\n"{instance.content}"'
        from_email = settings.DEFAULT_FROM_EMAIL
        superuser_emails = [user.email for user in User.objects.filter(is_superuser=True, is_active=True)]

        if superuser_emails:
            send_mail(subject, message, from_email, superuser_emails, fail_silently=False)
