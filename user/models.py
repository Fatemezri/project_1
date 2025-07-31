from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_jalali.db import models as jmodels
from django.db import models



class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError("شماره همراه یا ایمیل خود را وارد کنید")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password) #هش کردن رمز
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email=email, password=password, **extra_fields)



class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('نام کاربر', max_length=30, unique=True)
    email = models.EmailField('ایمیل', unique=True, null=True,blank=True)  # unique: no duplicates, null: DB can store NULL, blank: form allows empty
    phone = models.CharField('شماره همراه', max_length=20, unique=True, null=True, blank=True)
    is_active = models.BooleanField('فعال', default=True)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام", null=True)
    updated_at = jmodels.jDateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی", null=True)
    is_staff = models.BooleanField('ادمین', default=False)
    slug = models.SlugField(unique=True, blank=True)  # null=False by default, better to omit it explicitly

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # customize as you need


    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربرها '

    def save(self, *args, **kwargs):
        # Optional: auto-generate slug if empty
        if not self.slug and self.username:
            from django.utils.text import slugify
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)


class MassEmail(models.Model):
    subject = models.CharField('عنوان',max_length=255)
    html_message = models.TextField()
    created_at = models.DateTimeField('زمان ارسال',auto_now_add=True)

    class Meta:
        verbose_name = ' ایمیل'
        verbose_name_plural = 'ایمیل '


    def __str__(self):
        return self.subject


class MediaFile(models.Model):
    file = models.FileField(upload_to='uploads/', verbose_name="نام فایل")
    is_minified = models.BooleanField(default=False, verbose_name="مینیفای")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ آپلود")

    def delete(self, *args, **kwargs):
        from .utils import delete_file_from_arvan
        if self.file:
            delete_file_from_arvan(self.file.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = 'فایل'
        verbose_name_plural = 'فایل‌ها'