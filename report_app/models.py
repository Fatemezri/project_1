# D:\PROJECT\MIZAN_GOSTAR\PROJECT\REPORT\models.py

import logging
from django.db import models
from django.conf import settings

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)

class Message(models.Model):
    """مدل برای پیام‌های داخلی بین مدیران و سوپریوزرها."""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
        override save method to add logging.
        """
        try:
            is_new = self.pk is None
            super().save(*args, **kwargs)
            if is_new:
                logger.info(f"✅ New message (ID: {self.pk}) sent from '{self.sender.username}' to '{self.recipient.username}'.")
            else:
                logger.info(f"🔄 Message (ID: {self.pk}) from '{self.sender.username}' to '{self.recipient.username}' updated. is_read status: {self.is_read}.")
        except Exception as e:
            logger.error(f"❌ Error saving message from '{self.sender.username}': {e}", exc_info=True)
            raise

    def delete(self, *args, **kwargs):
        """
        override delete method to add logging.
        """
        logger.info(f"Attempting to delete message (ID: {self.pk}) from '{self.sender.username}' to '{self.recipient.username}'.")
        try:
            super().delete(*args, **kwargs)
            logger.info(f"✅ Message (ID: {self.pk}) from '{self.sender.username}' to '{self.recipient.username}' deleted successfully.")
        except Exception as e:
            logger.error(f"❌ Error deleting message (ID: {self.pk}) from '{self.sender.username}': {e}", exc_info=True)
            raise

    def __str__(self):
        return f'پیام از {self.sender.username} به {self.recipient.username}'
