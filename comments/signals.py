# comments/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Comment, Notification
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

@receiver(post_save, sender=Comment)
def create_moderator_report_notification(sender, instance, created, **kwargs):
    """
    این سیگنال بعد از ذخیره شدن یک کامنت فعال می‌شود.
    اگر گزارش ناظر برای کامنت ارسال شده باشد، یک اعلان برای سوپریوزر ایجاد می‌کند.
    """
    # بررسی می‌کنیم که آیا فیلد moderator_report اخیراً تغییر کرده است یا خیر
    if instance.moderator_report and kwargs.get('update_fields') and 'moderator_report' in kwargs['update_fields']:
        # سوپریوزر را پیدا می‌کنیم
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                # اعلان جدید را ایجاد می‌کنیم
                Notification.objects.create(
                    recipient=superuser,
                    sender=instance.user,  # یا sender را null بگذارید چون ناظر است
                    notification_type='moderator_report',
                    message=f"ناظر {instance.user.username} گزارشی برای نظر کاربر {instance.user.username} ارسال کرد.",
                    related_comment=instance
                )

                # می‌توانید یک LogEntry هم برای نمایش در پنل اصلی ادمین اضافه کنید
                LogEntry.objects.log_action(
                    user_id=superuser.pk,
                    content_type_id=ContentType.objects.get_for_model(Notification).pk,
                    object_id=superuser.pk,
                    object_repr="گزارش جدید ناظر",
                    action_flag=ADDITION,
                    change_message="یک گزارش جدید از طرف ناظر ارسال شد."
                )
        except Exception as e:
            # در صورت بروز خطا، آن را در کنسول نمایش دهید
            print(f"خطا در ارسال اعلان به سوپریوزر: {e}")