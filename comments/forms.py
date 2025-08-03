from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'متن نظر',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'اینجا نظر خود را بنویسید...'
            }),
        }
