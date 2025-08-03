from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    """
    مدل برای ذخیره نظرات کاربران.
    """
    STATUS_CHOICES = (
        ('pending', 'در انتظار بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='کاربر')
    text = models.TextField(verbose_name='متن')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    moderator_report = models.TextField(blank=True, null=True,
                                        help_text="گزارش ناظر برای سوپریوزر.", verbose_name='گزارش ناظر')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        permissions = (
            ("can_moderate_comments", "Can moderate comments"),
        )

    def __str__(self):
        return f"نظر از {self.user.username} در تاریخ {self.created_at.strftime('%Y-%m-%d')}"


class Notification(models.Model):
    """
    مدل برای ذخیره اعلان‌های داخلی برای مدیران.
    """
    NOTIFICATION_CHOICES = (
        ('new_comment', 'نظر جدید'),
        ('comment_approved', 'نظر تایید شده'),
        ('moderator_report', 'گزارش ناظر'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='گیرنده')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='فرستنده')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_CHOICES, verbose_name='نوع اعلان')
    message = models.TextField(verbose_name='پیام')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    related_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name='نظر مرتبط')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"

    def __str__(self):
        return f"اعلان برای {self.recipient.username}: {self.get_notification_type_display()}"


@receiver(post_save, sender=Comment)
def create_moderator_notification(sender, instance, created, **kwargs):
    """
    پس از ایجاد یک نظر جدید، یک اعلان برای تمام ناظران ارسال می‌کند.
    """
    if created and instance.status == 'pending':
        moderators = User.objects.filter(groups__name='Moderators')
        for moderator in moderators:
            Notification.objects.create(
                recipient=moderator,
                sender=instance.user,
                notification_type='new_comment',
                message=f"نظر جدیدی از {instance.user.username} در انتظار بررسی است.",
                related_comment=instance
            )
