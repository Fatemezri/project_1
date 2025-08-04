import logging
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django_jalali.db import models as jmodels
from django.db import models
from django.utils.text import slugify
from .signals import good_evening_email_sent_signal, good_evening_email_failed_signal, user_registered_signal

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            logger.error("❌ User creation failed: Email or phone number must be provided.")
            raise ValueError("شماره همراه یا ایمیل خود را وارد کنید")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)  # هش کردن رمز
        user.save()

        logger.info(f"✅ User created successfully: '{username}' (email: {email}, phone: {phone}).")
        user_registered_signal.send(sender=self.__class__, user=user)

        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            logger.error("❌ Superuser creation failed: 'is_staff' must be True.")
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            logger.error("❌ Superuser creation failed: 'is_superuser' must be True.")
            raise ValueError("Superuser must have is_superuser=True.")

        superuser = self.create_user(username, email=email, password=password, **extra_fields)
        logger.info(f"⭐️ Superuser created successfully: '{username}' (email: {email}).")

        return superuser


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField('نام کاربر', max_length=30, unique=True)
    email = models.EmailField('ایمیل', unique=True, null=True, blank=True)
    phone = models.CharField('شماره همراه', max_length=20, unique=True, null=True, blank=True)
    is_active = models.BooleanField('فعال', default=True)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام", null=True)
    updated_at = jmodels.jDateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی", null=True)
    is_staff = models.BooleanField('ادمین', default=False)
    slug = models.SlugField(unique=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربرها '

    def save(self, *args, **kwargs):
        if not self.slug and self.username:
            self.slug = slugify(self.username)
            logger.info(f"Generated slug '{self.slug}' for user '{self.username}'.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class MassEmail(models.Model):
    subject = models.CharField('عنوان', max_length=255)
    html_message = models.TextField()
    created_at = models.DateTimeField('زمان ارسال', auto_now_add=True)

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
        if self.file:
            try:
                from .utils import delete_file_from_arvan
                logger.info(f"Attempting to delete file '{self.file.name}' from ArvanCloud.")
                delete_file_from_arvan(self.file.name)
                logger.info(f"File '{self.file.name}' successfully deleted from ArvanCloud.")
            except Exception as e:
                logger.error(f"❌ Error deleting file '{self.file.name}' from ArvanCloud: {e}", exc_info=True)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = 'فایل'
        verbose_name_plural = 'فایل‌ها'


class SystemNotification(models.Model):
    message = models.TextField(verbose_name="پیام")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان")
    level = models.CharField(max_length=20, default='info', verbose_name="سطح")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "نوتیفیکیشن سیستم"
        verbose_name_plural = "نوتیفیکیشن‌های سیستم"

    def __str__(self):
        return f"{self.level}: {self.message[:50]}..."


def create_sent_email_notification(sender, count, **kwargs):
    try:
        SystemNotification.objects.create(
            message=f"ایمیل 'عصر بخیر' با موفقیت برای {count} کاربر ارسال شد.",
            level='info'
        )
        logger.info(f"Notification created: Email 'Good evening' sent to {count} users.")
    except Exception as e:
        logger.error(f"❌ Failed to create SystemNotification for successful email send: {e}", exc_info=True)


def create_failed_email_notification(sender, error, **kwargs):
    try:
        SystemNotification.objects.create(
            message=f"خطا در ارسال ایمیل 'عصر بخیر': {error}",
            level='error'
        )
        logger.error(f"❌ Notification created: Email sending failed with error: {error}")
    except Exception as e:
        logger.error(f"❌ Failed to create SystemNotification for failed email send: {e}", exc_info=True)


good_evening_email_sent_signal.connect(create_sent_email_notification)
good_evening_email_failed_signal.connect(create_failed_email_notification)
