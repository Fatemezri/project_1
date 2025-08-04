# D:\PROJECT\MIZAN_GOSTAR\PROJECT\COMMENT\forms.py

import logging
from django import forms
from .models import Comment
from django.core.exceptions import ValidationError

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class CommentForm(forms.ModelForm):
    """فرم برای کاربران جهت ثبت کامنت."""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_content(self):
        """
        این متد برای اعتبارسنجی فیلد 'content' استفاده می‌شود.
        """
        content = self.cleaned_data.get('content')
        logger.debug("Running clean_content for the comment form.")

        if len(content.strip()) < 5:
            logger.warning("Comment content is too short (less than 5 characters).")
            raise ValidationError("محتوای کامنت باید حداقل ۵ کاراکتر باشد.")

        logger.info("Comment content validation successful.")
        return content
