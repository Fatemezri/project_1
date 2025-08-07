from django.conf import settings
from django.db import models

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='فرستنده'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='گیرنده'
    )
    content = models.TextField(verbose_name='متن پیام')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')

    def __str__(self):
        return f'پیام از {self.sender.username} به {self.recipient.username}'

    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'