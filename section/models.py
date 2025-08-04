import logging
from django.db import models
from django.core.exceptions import ValidationError

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class Section(models.Model):
    """مدل برای سکشن‌ها با ساختار درختی و محدودیت سطح."""
    title = models.CharField(max_length=100, verbose_name="عنوان")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="children", verbose_name="والد"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "سکشن"
        verbose_name_plural = "سکشن‌ها"
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_level(self):
        """تعیین عمق سکشن (حداکثر 3 سطح مجاز)."""
        logger.debug(f"Calculating level for section '{self.title}' (ID: {self.pk}).")
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        logger.debug(f"Section '{self.title}' is at level {level}.")
        return level

    def clean(self):
        """اعتبارسنجی‌های قبل از ذخیره (برای فرم‌های ModelForm و Save)."""
        super().clean()
        logger.info(f"Running custom clean validation for section '{self.title}'.")

        # اعتبارسنجی سطح (فقط برای سکشن‌های موجود)
        if self.pk:
            if self.get_level() > 2:
                logger.warning(f"❌ Validation failed for section '{self.title}': level exceeds 2.")
                raise ValidationError("سکشن‌ها فقط تا سه سطح مجاز هستند. (سطح 0، 1 و 2)")

        # اعتبارسنجی حداکثر تعداد سکشن (فقط برای سکشن‌های جدید)
        if not self.pk and Section.objects.count() >= 7:
            logger.warning("❌ Validation failed: maximum number of sections (7) has been reached.")
            raise ValidationError("حداکثر ۷ سکشن مجاز است.")

    def save(self, *args, **kwargs):
        """override save method to add logging."""
        try:
            is_new = self.pk is None
            super().save(*args, **kwargs)
            if is_new:
                logger.info(f"✅ New section '{self.title}' created successfully.")
            else:
                logger.info(f"🔄 Section '{self.title}' (ID: {self.pk}) updated successfully.")
        except Exception as e:
            logger.error(f"❌ Error saving section '{self.title}': {e}", exc_info=True)
            raise

    def delete(self, *args, **kwargs):
        """override delete method to add logging."""
        logger.info(f"Attempting to delete section '{self.title}' (ID: {self.pk}).")
        try:
            super().delete(*args, **kwargs)
            logger.info(f"✅ Section '{self.title}' (ID: {self.pk}) deleted successfully.")
        except Exception as e:
            logger.error(f"❌ Error deleting section '{self.title}' (ID: {self.pk}): {e}", exc_info=True)
            raise
