from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()

def notify_moderators(comment):
    moderators = User.objects.filter(groups__name='Moderators')
    for moderator in moderators:
        send_mail(
            subject='کامنت جدید نیاز به بررسی دارد',
            message=f'یک کامنت جدید توسط کاربر {comment.user.username} ارسال شده است:\n\n"{comment.text}"\n\nلطفاً برای بررسی وارد پنل مدیریت شوید.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[User.email],
            fail_silently=False
                    )

def notify_superuser(comment):
    superusers = User.objects.filter(is_superuser=True)
    for superuser in superusers:
        send_mail(
            subject='کامنت تأیید شده',
            message=f'کامنت زیر توسط ناظر تأیید شده است:\n\n"{comment.text}"\n\nتأیید شده توسط: {comment.user.username}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[User.email],
            fail_silently=False
                    )
