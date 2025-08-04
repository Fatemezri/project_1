# your_app/models.py
from django.db import models
from django.core.exceptions import ValidationError

class Section(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="children", verbose_name="والد"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "سکشن"
        verbose_name_plural = "سکشن‌ها"
        ordering = ['order'] # برای اطمینان از اعمال ترتیب در کوئری‌ها

    def __str__(self):
        return self.title

    def get_level(self):
        """تعیین عمق سکشن (حداکثر 3 سطح مجاز)"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def clean(self):
        """اعتبارسنجی‌های قبل از ذخیره (برای فرم‌های ModelForm و Save)"""
        super().clean() # فراخوانی clean متد والد


        if self.pk:
            if self.get_level() > 2:
                raise ValidationError("سکشن‌ها فقط تا سه سطح مجاز هستند. (سطح 0، 1 و 2)")


        if not self.pk and Section.objects.count() >= 7:
            raise ValidationError("حداکثر ۷ سکشن مجاز است.")