from django.db import models
from django.core.exceptions import ValidationError

class Section(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name="والد"
    )
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True, verbose_name="ترتیب نمایش")

    def __str__(self):
        return self.title

    def get_level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def clean(self):
        if self.get_level() > 2:
            raise ValidationError("سکشن‌ها فقط تا سه سطح مجاز هستند.")
        if Section.objects.count() >= 7 and not self.pk:
            raise ValidationError("حداکثر ۷ سکشن مجاز است.")

    class Meta:
        verbose_name = "سکشن"
        verbose_name_plural = "سکشن‌ها"
        ordering = ['order']