from django.contrib.auth import get_user_model
user = get_user_model()
from django.core.validators import validate_email
import hashlib
import logging
from django.core.exceptions import ValidationError
from .models import CustomUser
import re
from .models import MediaFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image
from .utils import upload_file_to_arvan, delete_file_from_arvan
logger = logging.getLogger(__name__)
from django import forms
from ckeditor.widgets import CKEditorWidget
logger = logging.getLogger('user')


class SendEmailForm(forms.Form):
    subject = forms.CharField(
        max_length=255,
        label="عنوان ایمیل",
        help_text="مثلاً: خوش‌آمدگویی به کاربر جدید",
        error_messages={
            'required': 'لطفاً عنوان ایمیل را وارد کنید.',
            'max_length': 'عنوان ایمیل نمی‌تواند بیش از ۲۵۵ کاراکتر باشد.',
        }
    )

    body = forms.CharField(
        widget=CKEditorWidget(),
        label="متن ایمیل",
        help_text="متن کامل ایمیل را با استفاده از ویرایشگر وارد کنید.",
        error_messages={
            'required': 'متن ایمیل نمی‌تواند خالی باشد.',
        }
    )



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
                logger.debug(f"📧 Valid email login attempt: {contact}")
                return contact
            except ValidationError:
                logger.warning(f"❌ Invalid email format entered: {contact}")
                raise forms.ValidationError("ایمیل وارد شده معتبر نیست.")

        # در غیر این صورت، فرض می‌کنیم شماره موبایل باشه
        contact = re.sub(r'\D', '', contact)

        if contact.startswith('98') and len(contact) == 12:
            contact = '0' + contact[2:]

        if re.match(r'^09\d{9}$', contact):
            logger.debug(f"📱 Valid phone login attempt: {contact}")
            return contact

        logger.warning(f"❌ Invalid contact info entered: {contact}")
        raise forms.ValidationError("شماره موبایل/ایمیل معتبر نیست.")




class signinForm(forms.ModelForm):
    contact = forms.CharField(
        label='ایمیل/شماره همراه',
        required=True,
        error_messages={'required': 'این فیلد اجباری است!'},
        widget=forms.TextInput(attrs={'placeholder': '...ایمیل یا شماره'})
    )
    password = forms.CharField(
        label='رمز عبور اول',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز اول'})
    )
    confirm_password = forms.CharField(
        label='تکرار رمز عبور اول',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز اول'})
    )
    second_password = forms.CharField(
        label='رمز دوم',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز دوم'})
    )
    confirm_second_password = forms.CharField(
        label='تکرار رمز دوم',
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز دوم'})
    )

    class Meta:
        model = CustomUser
        fields = ['username']



    def clean(self):
        cleaned_data = super().clean()
        contact = cleaned_data.get("contact")
        logger.debug(f"Starting validation for contact: {contact}")

        if '@' in contact:
            cleaned_data['email'] = contact
            cleaned_data['phone'] = None
            if CustomUser.objects.filter(email=contact).exists():
                logger.warning(f"Duplicate email registration attempt: {contact}")
                raise ValidationError("کاربری با این ایمیل قبلاً ثبت‌نام کرده است.")
        elif re.match(r'^09\d{9}$', contact):
            cleaned_data['phone'] = contact
            cleaned_data['email'] = None
            if CustomUser.objects.filter(phone=contact).exists():
                logger.warning(f"Duplicate phone registration attempt: {contact}")
                raise ValidationError("کاربری با این شماره همراه قبلاً ثبت‌نام کرده است.")

        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("confirm_password")
        second1 = cleaned_data.get("second_password")
        second2 = cleaned_data.get("confirm_second_password")
        contact = cleaned_data.get("contact")

        # بررسی رمز اول
        if password1 and password2 and password1 != password2:
            logger.warning("First password and confirmation do not match.")
            raise ValidationError("رمز اول و تکرار آن یکسان نیستند.")

        # بررسی رمز دوم
        if second1 and second2:
            if second1 != second2:
                logger.warning("Second password and confirmation do not match.")
                raise ValidationError("رمز دوم و تکرار آن یکسان نیستند.")
        else:
            logger.warning("Second password missing.")
            raise ValidationError("وارد کردن رمز دوم الزامی است.")

        # بررسی شماره یا ایمیل
        if contact:
            if '@' in contact:
                cleaned_data['email'] = contact
                cleaned_data['phone'] = None
            elif re.match(r'^09\d{9}$', contact):
                cleaned_data['phone'] = contact
                cleaned_data['email'] = None
            else:
                logger.warning(f"Invalid email or phone format: {contact}")
                raise ValidationError("ایمیل یا شماره همراه معتبر نیست")

        logger.info(f"Signup form validated successfully for contact: {contact}")
        return cleaned_data

    def get_hashed_second_password(self):
        second_password = self.cleaned_data.get("second_password")
        if second_password:
            hashed = hashlib.sha256(second_password.encode()).hexdigest()
            logger.info(f"Second password hashed successfully for contact: {self.cleaned_data.get('contact')}")
            logger.debug(f"Hashed value (truncated): {hashed[:10]}...")
            return hashed
        return None



class passwordResetForm(forms.Form):
    contact = forms.CharField(
        label='ایمیل/شماره همراه',
        widget=forms.TextInput(attrs={'placeholder': '...ایمیل یا شماره'})
    )

    def clean_contact(self):
        contact = self.cleaned_data['contact'].strip()
        logger.debug(f"Password reset requested for: {contact}")


        if '@' in contact:
            try:
                validate_email(contact)
                logger.info(f"Valid email for password reset: {contact}")
                return contact
            except ValidationError:
                logger.warning(f"Invalid email format: {contact}")
                raise ValidationError("ایمیل وارد شده معتبر نیست.")

        # اگر شماره موبایل بود
        contact = re.sub(r'\D', '', contact)
        if contact.startswith('98') and len(contact) == 12:
            contact = '0' + contact[2:]

        if re.match(r'^09\d{9}$', contact):
            logger.info(f"Valid phone number for password reset: {contact}")
            return contact

        logger.warning(f"Invalid contact format: {contact}")
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
    logger.debug("Validating new password and confirmation...")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            logger.warning("Password and confirmation do not match.")
            raise forms.ValidationError("رمزهای عبور با هم مطابقت ندارند.")
        logger.info("New password validated successfully.")
        return cleaned_data




class MediaFileAdminForm(forms.ModelForm):
    upload = forms.FileField(required=False, label="آپلود فایل جدید")

    class Meta:
        model = MediaFile
        fields = ['is_minified']

    def recursive_minify(self, image_file, max_kb=300):
        image = Image.open(image_file)
        image = image.convert("RGB")
        qualities = (85, 40, 10)

        logger.debug(f"Starting recursive minify for file: {getattr(image_file, 'name', 'unknown')}")

        for q in qualities:
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=q)
            size_kb = buffer.getbuffer().nbytes / 1024

            logger.debug(f"Minify attempt at quality={q}, size={size_kb:.2f}KB")

            if size_kb <= max_kb:
                logger.info(f"Image successfully minified at quality={q}, final size={size_kb:.2f}KB")
                buffer.seek(0)
                return InMemoryUploadedFile(
                    buffer,
                    None,
                    f"min_{getattr(image_file, 'name', 'image.jpg')}",
                    'image/jpeg',
                    buffer.getbuffer().nbytes,
                    None
                )

        logger.warning("Image could not be reduced below max_kb limit, returning final version.")

        buffer.seek(0)
        return InMemoryUploadedFile(
            buffer,
            None,
            f"min_{getattr(image_file, 'name', 'image.jpg')}",
            'image/jpeg',
            buffer.getbuffer().nbytes,
            None
        )

    def save(self, commit=True):
        upload_file = self.cleaned_data.get("upload")
        is_minified = self.cleaned_data.get("is_minified")
        instance = super().save(commit=False)

        logger.debug(f"Saving MediaFile instance: minify={is_minified}, upload_provided={bool(upload_file)}")

        if upload_file:
            if instance.pk and instance.file:
                logger.info(f"Deleting old file from Arvan: {instance.file.name}")
                delete_file_from_arvan(instance.file.name)


            if is_minified and upload_file.name.lower().endswith(('jpg', 'jpeg', 'png', 'webp')):
                logger.debug(f"File is an image and minify requested. Proceeding to minify: {upload_file.name}")
                upload_file = self.recursive_minify(upload_file)

            path = f"uploads/{upload_file.name}"
            success = upload_file_to_arvan(upload_file, path)
            if success:
                logger.info(f"File uploaded successfully to Arvan at path: {path}")
                instance.file.name = path
            else:
                logger.error(f"File upload to Arvan failed: {upload_file.name}")

        if commit:
            instance.save()
            logger.debug(f"MediaFile instance saved: {instance.pk}")

        return instance