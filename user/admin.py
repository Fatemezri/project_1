from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile
from .forms import MediaFileAdminForm
from .utils import upload_file_to_arvan, delete_file_from_arvan, generate_presigned_url



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
import jdatetime


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        'username',
        'is_active',
        'is_staff',
        'created_at',
        'updated_at',
    )

    readonly_fields = ('created_at', 'updated_at', 'slug')

    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'phone', 'password')
        }),

        ('تاریخ‌ها و سیستم', {
            'fields': ('created_at', 'updated_at', 'slug'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    def get_jalali_created(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d - %H:%M')
        return "-"

    def get_jalali_updated(self, obj):
        if obj.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.updated_at).strftime('%Y/%m/%d - %H:%M')
        return "-"

    get_jalali_created.short_description = 'تاریخ ثبت‌نام'
    get_jalali_updated.short_description = 'آخرین بروزرسانی'


    def get_jalali_updated(self, obj):
        if obj.updated_at:
            gregorian = obj.updated_at
            jalali = jdatetime.datetime.fromgregorian(datetime=gregorian)
            return jalali.strftime('%Y/%m/%d - %H:%M')
        return "-"

    get_jalali_created.short_description = 'تاریخ ثبت‌نام'
    get_jalali_updated.short_description = 'آخرین بروزرسانی'

admin.site.register(CustomUser, CustomUserAdmin)


class MassEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_at']
    actions = ['send_email_to_all']

    def send_email_to_all(self, request, queryset):

        subject = mass_email.subject
        html_message = mass_email.html_message
        from_email = settings.DEFAULT_FROM_EMAIL

        # همه کاربرانی که ایمیل دارند
        recipients = CustomUser.objects.exclude(email='').values_list('email', flat=True)

        if not recipients:
            self.message_user(request, "هیچ کاربری با ایمیل معتبر یافت نشد.", level=messages.WARNING)
            return

        # ساخت و ارسال ایمیل
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=[],
            bcc=recipients,  # ایمیل به صورت BCC ارسال شود تا لیست دیده نشود
        )
        email.content_subtype = "html"

        try:
            email.send()
            self.message_user(request, f"{len(recipients)} ایمیل با موفقیت ارسال شد.", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"خطا در ارسال ایمیل: {str(e)}", level=messages.ERROR)

    send_email_to_all.short_description = "ارسال ایمیل به همه کاربران"

admin.site.register(MassEmail, MassEmailAdmin)


from django.utils.html import format_html



class MediaFileAdmin(admin.ModelAdmin):
    form = MediaFileAdminForm
    list_display = ['file_link', 'is_minified', 'uploaded_at', 'download_link']
    readonly_fields = ['download_link']

    def file_link(self, obj):
        return obj.file.name
    file_link.short_description = "نام فایل"

    def download_link(self, obj):
        if obj.file and obj.file.name:
            url = generate_presigned_url(obj.file.name)
            return format_html(f"<a href='{url}' target='_blank'>دانلود</a>")
        return "فایلی وجود ندارد"
    download_link.short_description = "دانلود فایل"

    def delete_model(self, request, obj):
        delete_file_from_arvan(obj.file.name)
        super().delete_model(request, obj)

    # ❌ این تابع دیگه فایل رو مدیریت نمی‌کنه
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

# Register your models here.
