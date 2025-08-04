
import logging
from django.db import models
from django.conf import settings

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)

class Comment(models.Model):
    """مدل برای ذخیره کامنت‌های کاربران."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """
         override save method to add logging.
        """
        try:
            is_new = self.pk is None
            super().save(*args, **kwargs)
            if is_new:
                logger.info(f"✅ New comment from user '{self.user.username}' (ID: {self.user.id}) saved successfully. Status: {'Approved' if self.is_approved else 'Pending'}.")
            else:
                logger.info(f"🔄 Comment with ID '{self.pk}' from user '{self.user.username}' updated. Status: {'Approved' if self.is_approved else 'Pending'}.")
        except Exception as e:
            logger.error(f"❌ Error saving comment from user '{self.user.username}': {e}", exc_info=True)
            raise

    def delete(self, *args, **kwargs):
        """
        override delete method to add logging.
        """
        logger.info(f"Attempting to delete comment with ID '{self.pk}' from user '{self.user.username}'.")
        try:
            super().delete(*args, **kwargs)
            logger.info(f"✅ Comment with ID '{self.pk}' from user '{self.user.username}' deleted successfully.")
        except Exception as e:
            logger.error(f"❌ Error deleting comment with ID '{self.pk}' from user '{self.user.username}': {e}", exc_info=True)
            raise

    def __str__(self):
        return f'کامنت از طرف {self.user.username}'
