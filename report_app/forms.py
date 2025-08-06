from django import forms
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageAdminForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'content']  # Intentionally exclude 'is_read'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show non-superusers (moderators) as senders
        self.fields['sender'].queryset = User.objects.filter(groups__name='MessageAdmins', is_superuser=False)

        # Only show superusers as recipients
        self.fields['recipient'].queryset = User.objects.filter(is_superuser=True)

        self.fields['sender'].label = 'فرستنده'
        self.fields['recipient'].label = 'گیرنده'
        self.fields['content'].label = 'متن گزارش'
