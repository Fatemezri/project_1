# comment/notifications.py
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

User = get_user_model()

def notify_moderators(comment):
    moderators = User.objects.filter(groups__name='Moderators')
    for moderator in moderators:
        send_mail(
            'کامنت جدید نیاز به بررسی دارد',
            f'کامنت جدید: "{comment.content}" از طرف {comment.user}',
            'no-reply@example.com',
            [moderator.email],
        )

def notify_superuser(comment):
    superusers = User.objects.filter(is_superuser=True)
    for superuser in superusers:
        send_mail(
            'کامنت تایید شد',
            f'کامنت "{comment.content}" توسط {comment.moderator} تایید شد.',
            'no-reply@example.com',
            [superuser.email],
        )
