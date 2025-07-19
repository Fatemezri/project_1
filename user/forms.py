from django import forms
from django.contrib.auth import get_user_model
user = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(
        label="نام کاربری",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'نام کاربری'})
    )
    contact = forms.CharField(
        label="ایمیل یا شماره موبایل",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'ایمیل یا شماره همراه'})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'})
    )

    def clean_contact(self):
        contact = self.cleaned_data['contact']
        # اعتبارسنجی ساده:
        if "@" in contact:
            return contact
        elif contact.isdigit():
            return contact
        raise forms.ValidationError("ایمیل یا شماره تلفن معتبر وارد کنید.")


