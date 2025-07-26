from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


@shared_task
def send_evening_email():
    User = get_user_model()
    for user in User.objects.all():
        if user.email:
            send_mail(
                'پیام عصر بخیر',
                'سلام! وقت بخیر. این ایمیل خودکار برای شما ارسال شده تا عصر خوبی داشته باشید.',
                'your_email@example.com',
                [user.email],
                fail_silently=True,
            )
