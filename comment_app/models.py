from django.db import models
from django.conf import settings
from slugify import slugify
from django.utils.text import Truncator


class Comment(models.Model):
    """مدلی برای ذخیرهٔ کامنت‌های کاربران."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='کاربر'
    )
    content = models.TextField(verbose_name='متن کامنت')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='اسلاگ'
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name='تأیید شده'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت‌ها'

    def __str__(self):
        return f'کامنت از طرف {self.user.username}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                Truncator(self.content).chars(40),
                lowercase=True,
                separator='-',
                regex_pattern=r'[^ا-یءآa-zA-Z0-9]+'
            )
            unique_slug = base_slug
            num = 1
            while Comment.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)
