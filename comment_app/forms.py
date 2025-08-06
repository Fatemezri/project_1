from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """فرم برای کاربران جهت ثبت کامنت."""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }