from django import forms
from django.contrib.auth import get_user_model
user = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(
        label="نام کاربری",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    contact = forms.CharField(
        label="ایمیل یا شماره موبایل",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'Email یا Phone'})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        # اعتبارسنجی ساده:
        if "@" in contact:
            # یعنی ایمیله
            return contact
        elif contact.isdigit():
            # یعنی شماره تلفنه
            return contact
        raise forms.ValidationError("ایمیل یا شماره تلفن معتبر وارد کنید.")


