# user/tasks.py (یا هر اپلیکیشنی که مربوط به کاربران شماست)
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model # برای گرفتن مدل کاربر
from django.utils import timezone

@shared_task
def send_good_evening_email_task():
    User = get_user_model()
    # فقط کاربران فعال و دارای ایمیل رو انتخاب کنید
    users = User.objects.filter(is_active=True).exclude(email__isnull=True).exclude(email__exact='')

    if not users:
        print("No active users with email found to send good evening message.")
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
        print(f"Successfully sent good evening email to {len(recipient_list)} users at {timezone.now()}")
        # اینجا میتونید سیگنال مربوط به ارسال موفقیت آمیز رو هم تریگر کنید
        # مثلاً: good_evening_email_sent_signal.send(sender=None, count=len(recipient_list))
    except Exception as e:
        print(f"Error sending good evening email: {e}")
