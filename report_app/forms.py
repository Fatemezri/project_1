from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """فرم برای مدیران پیام جهت ارسال پیام‌های داخلی."""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
