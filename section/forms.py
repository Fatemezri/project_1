import logging
from django import forms
from .models import Section

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = "__all__"

    def clean(self):
        """
        این متد برای اعتبارسنجی‌های مربوط به فرم ادمین استفاده می‌شود.
        """
        cleaned_data = super().clean()
        logger.info(f"Running clean method for SectionAdminForm.")

        # اعتبارسنجی حداکثر تعداد سکشن (فقط برای سکشن‌های جدید)
        if not self.instance.pk and Section.objects.count() >= 7:
            logger.warning("❌ Validation failed: maximum number of sections (7) has been reached.")
            raise forms.ValidationError("حداکثر ۷ سکشن قابل افزودن است.")

        # اعتبارسنجی عمق سکشن
        parent = cleaned_data.get('parent')
        current_level = 0
        if parent:
            current_level = parent.get_level() + 1  # سطح فعلی = سطح والد + 1

        if current_level > 2:
            logger.warning(f"❌ Validation failed for section: parent '{parent.title}' leads to a level greater than 2.")
            raise forms.ValidationError("عمق بیش از ۳ سطح مجاز نیست. (سطح 0، 1 و 2)")

        logger.info("✅ SectionAdminForm validation successful.")
        return cleaned_data
