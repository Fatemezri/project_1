import logging
from django import forms
from .models import Message
from django.core.exceptions import ValidationError

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class MessageForm(forms.ModelForm):
    """فرم برای مدیران پیام جهت ارسال پیام‌های داخلی."""

    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_content(self):
        """
        این متد برای اعتبارسنجی فیلد 'content' استفاده می‌شود.
        """
        content = self.cleaned_data.get('content')
        logger.debug("Running clean_content for the message form.")

        if len(content.strip()) < 10:
            logger.warning("Message content is too short (less than 10 characters).")
            raise ValidationError("محتوای پیام باید حداقل ۱۰ کاراکتر باشد.")

        logger.info("Message content validation successful.")
        return content
