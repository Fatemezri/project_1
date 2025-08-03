from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Comment(models.Model):
    """
    مدل مربوط به نظرات کاربران.
    """
    STATUS_CHOICES = (
        ('pending', 'در انتظار تأیید'),
        ('approved', 'تأیید شده'),
        ('rejected', 'رد شده'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='کاربر')
    text = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    moderator_report = models.TextField(
        blank=True,
        null=True,
        verbose_name='گزارش ناظر',
        help_text="گزارش ناظر برای مدیر ارشد"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        permissions = (
            ("can_moderate_comments", "اجازه‌ی بررسی نظرات"),
        )

    def __str__(self):
        return f"نظر توسط {self.user.username} در تاریخ {self.created_at.strftime('%Y-%m-%d')}"


class Notification(models.Model):
    """
    مدل ذخیره‌سازی اعلان‌های داخلی برای ادمین‌ها.
    """
    NOTIFICATION_CHOICES = (
        ('new_comment', 'نظر جدید'),
        ('comment_approved', 'نظر تأیید شده'),
        ('moderator_report', 'گزارش ناظر'),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='گیرنده'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='فرستنده'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_CHOICES,
        verbose_name='نوع اعلان'
    )
    message = models.TextField(verbose_name='متن اعلان')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده؟')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    related_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='نظر مرتبط'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"

    def __str__(self):
        return f"اعلان برای {self.recipient.username}: {self.get_notification_type_display()}"
