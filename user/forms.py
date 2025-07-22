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
        contact = self.cleaned_data['contact'].strip()

        # اگر ایمیل باشه
        if '@' in contact:
            try:
                validate_email(contact)
                return contact
            except ValidationError:
                raise forms.ValidationError("ایمیل وارد شده معتبر نیست.")

        # در غیر این صورت، فرض می‌کنیم شماره موبایل باشه
        contact = re.sub(r'\D', '', contact)

        if contact.startswith('98') and len(contact) == 12:
            contact = '0' + contact[2:]

        if re.match(r'^09\d{9}$', contact):
            return contact

        raise forms.ValidationError("شماره موبایل معتبر نیست.")


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
                raise ValidationError("ایمیل یا شماره همراه معتبر نیست.")
        return cleaned_data



class passwordResetForm(forms.Form):
    contact = forms.CharField(
        label='ایمیل/شماره همراه',
        widget=forms.TextInput(attrs={'placeholder': '...ایمیل یا شماره'})
    )

    def clean_contact(self):
        contact = self.cleaned_data['contact'].strip()

        # اگر ایمیل بود
        if '@' in contact:
            try:
                validate_email(contact)
                return contact
            except ValidationError:
                raise ValidationError("ایمیل وارد شده معتبر نیست.")

        # اگر شماره موبایل بود
        contact = re.sub(r'\D', '', contact)
        if contact.startswith('98') and len(contact) == 12:
            contact = '0' + contact[2:]

        if re.match(r'^09\d{9}$', contact):
            return contact

        raise ValidationError("ایمیل یا شماره همراه معتبر نیست.")


from django import forms

class PasswordChangeForm(forms.Form):
    new_password = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید'})
    )
    confirm_password = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("رمزهای عبور با هم مطابقت ندارند.")
        return cleaned_data
