from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager



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
    email = models.EmailField( 'ایمیل',unique=True, null=True, blank=True) # unique:ایمیل تکراری نباشه null:فیلد میتونه خالی باشه blanck: فرم میتونه خالی باشه
    phone = models.CharField( 'شماره همراه',max_length=20, unique=True, null=True, blank=True)
    is_active = models.BooleanField( 'فعال',default=True)
    is_staff = models.BooleanField('ادمین',default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # هنوز برای createsuperuser لازمه
    REQUIRED_FIELDS = ['email']  # برای ساختن ادمین

    def __str__(self):
        return self.username



