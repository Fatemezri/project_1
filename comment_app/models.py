from django.db import models
from django.conf import settings

class Comment(models.Model):
    """مدل برای ذخیره کامنت‌های کاربران."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'کامنت از طرف {self.user.username}'
