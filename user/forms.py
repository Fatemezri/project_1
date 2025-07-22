from django import forms
from django.contrib.auth import get_user_model
user = get_user_model()
from django.core.exceptions import ValidationError
from .models import CustomUser

class LoginForm(forms.Form):
    username = forms.CharField(
        label="نام کاربری",
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': 'نام کاربری'})
    )
    contact = forms.CharField(
        label="ایمیل یا شماره موبایل",
        max_length=50,
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



class signinForm(forms.ModelForm):
    contact = forms.CharField(
        label='ایمیل/شماره همراه',
        required=True,
        error_messages={'required': 'این فیلد اجباری است!'},
        widget=forms.TextInput(attrs={'placeholder': '...ایمیل یا شماره'})
    )
    password = forms.CharField(
        label='رمز عبور',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'})
    )
    confirm_password = forms.CharField(
        label='تکرار رمز عبور',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'})
    )

    class Meta:
        model = CustomUser
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise ValidationError("رمز عبور و تکرار آن یکسان نیستند.")

        contact = cleaned_data.get("contact")
        if contact:
            if '@' in contact:
                cleaned_data['email'] = contact
                cleaned_data['phone'] = None
            elif contact.isdigit():
                cleaned_data['phone'] = contact
                cleaned_data['email'] = None
            else:
                raise ValidationError("ایمیل یا شماره همراه شما معتبر نیست")

        return cleaned_data
