import logging
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from .models import CustomUser, MediaFile
from .utils import upload_file_to_arvan, delete_file_from_arvan
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


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
        logger.info(f"Cleaning contact field: '{contact}'")

        # اگر ایمیل باشه
        if '@' in contact:
            try:
                validate_email(contact)
                logger.info(f"Contact '{contact}' is a valid email.")
                return contact
            except ValidationError:
                logger.warning(f"Contact '{contact}' is an invalid email.")
                raise forms.ValidationError("ایمیل وارد شده معتبر نیست.")

        # در غیر این صورت، فرض می‌کنیم شماره موبایل باشه
        contact = re.sub(r'\D', '', contact)
        logger.info(f"Sanitized phone number: '{contact}'")

        if contact.startswith('98') and len(contact) == 12:
            contact = '0' + contact[2:]

        if re.match(r'^09\d{9}$', contact):
            logger.info(f"Contact '{contact}' is a valid Iranian phone number.")
            return contact

        logger.warning(f"Contact '{contact}' is an invalid phone number or email.")
        raise forms.ValidationError("شماره موبایل/ایمیل معتبر نیست.")


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
        contact = cleaned_data.get("contact")
        logger.info(f"Cleaning signin form for user '{cleaned_data.get('username')}' with contact '{contact}'.")

        if password and confirm and password != confirm:
            logger.warning("Password and confirmation password do not match.")
            raise ValidationError("رمز عبور و تکرار آن یکسان نیستند")

        if contact:
            if '@' in contact:
                cleaned_data['email'] = contact
                cleaned_data['phone'] = None
                logger.info(f"Contact '{contact}' identified as email.")
            elif re.match(r'^09\d{9}$', contact):  # شماره موبایل ایرانی
                cleaned_data['phone'] = contact
                cleaned_data['email'] = None
                logger.info(f"Contact '{contact}' identified as Iranian phone number.")
            else:
                logger.warning(f"Contact '{contact}' is not a valid email or phone number.")
                raise ValidationError("ایمیل یا شماره همراه معتبر نیست")
        return cleaned_data


class passwordResetForm(forms.Form):
    contact = forms.CharField(
        label='ایمیل/شماره همراه',
        widget=forms.TextInput(attrs={'placeholder': '...ایمیل یا شماره'})
    )

    def clean_contact(self):
        contact = self.cleaned_data['contact'].strip()
        logger.info(f"Cleaning password reset contact: '{contact}'")

        # اگر ایمیل بود
        if '@' in contact:
            try:
                validate_email(contact)
                logger.info(f"Contact '{contact}' is a valid email for password reset.")
                return contact
            except ValidationError:
                logger.warning(f"Contact '{contact}' is an invalid email for password reset.")
                raise ValidationError("ایمیل وارد شده معتبر نیست.")

        # اگر شماره موبایل بود
        contact = re.sub(r'\D', '', contact)
        if contact.startswith('98') and len(contact) == 12:
            contact = '0' + contact[2:]

        if re.match(r'^09\d{9}$', contact):
            logger.info(f"Contact '{contact}' is a valid phone number for password reset.")
            return contact

        logger.warning(f"Contact '{contact}' is an invalid email or phone number for password reset.")
        raise ValidationError("ایمیل یا شماره همراه معتبر نیست.")


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
        logger.info("Cleaning password change form.")
        if p1 and p2 and p1 != p2:
            logger.warning("New password and confirmation password do not match.")
            raise forms.ValidationError("رمزهای عبور با هم مطابقت ندارند.")
        return cleaned_data


class MediaFileAdminForm(forms.ModelForm):
    upload = forms.FileField(required=False, label="آپلود فایل جدید")

    class Meta:
        model = MediaFile
        fields = ['is_minified']

    def recursive_minify(self, image_file, max_kb=300):
        logger.info(f"Starting recursive minify for file '{getattr(image_file, 'name', 'N/A')}'.")
        try:
            image = Image.open(image_file)
            image = image.convert("RGB")
            qualities = (85, 40, 10)

            for q in qualities:
                buffer = BytesIO()
                image.save(buffer, format='JPEG', quality=q)
                size_kb = buffer.getbuffer().nbytes / 1024
                logger.info(f"Attempted minify with quality {q}, result size: {size_kb:.2f} KB.")

                if size_kb <= max_kb:
                    buffer.seek(0)
                    logger.info(f"Minify successful. Final quality: {q}, size: {size_kb:.2f} KB.")
                    return InMemoryUploadedFile(
                        buffer,
                        None,
                        f"min_{getattr(image_file, 'name', 'image.jpg')}",
                        'image/jpeg',
                        buffer.getbuffer().nbytes,
                        None
                    )

            # اگر هنوز بزرگ بود، آخرین نسخه رو برمی‌گردونه
            buffer.seek(0)
            logger.warning(f"Could not minify file to below {max_kb} KB. Returning lowest quality version.")
            return InMemoryUploadedFile(
                buffer,
                None,
                f"min_{getattr(image_file, 'name', 'image.jpg')}",
                'image/jpeg',
                buffer.getbuffer().nbytes,
                None
            )
        except Exception as e:
            logger.error(f"❌ Error during image minification: {e}", exc_info=True)
            return image_file

    def save(self, commit=True):
        upload_file = self.cleaned_data.get("upload")
        is_minified = self.cleaned_data.get("is_minified")
        instance = super().save(commit=False)
        logger.info(f"Saving MediaFile instance. New file uploaded: {bool(upload_file)}.")

        if upload_file:
            if instance.pk and instance.file:
                logger.info(f"Existing file '{instance.file.name}' found. Attempting to delete.")
                delete_file_from_arvan(instance.file.name)

            # اگر تصویر است و گزینه مینیفای فعال باشد:
            if is_minified and upload_file.name.lower().endswith(('jpg', 'jpeg', 'png', 'webp')):
                upload_file = self.recursive_minify(upload_file)
                logger.info(f"File '{upload_file.name}' processed for minification.")

            path = f"uploads/{upload_file.name}"
            success = upload_file_to_arvan(upload_file, path)
            if success:
                instance.file.name = path
                logger.info(f"File '{path}' successfully uploaded and assigned to instance.")
            else:
                logger.error(f"❌ File upload failed for '{path}'. Instance will not be saved with this file.")

        if commit:
            instance.save()
            logger.info("MediaFile instance saved to database.")
        return instance

