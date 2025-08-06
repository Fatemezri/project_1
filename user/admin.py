from django.contrib import  messages
from .models import MassEmail
from .models import MediaFile
from .forms import MediaFileAdminForm
from .utils import delete_file_from_arvan, generate_presigned_url
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ExportMixin
import os
import io
import arabic_reshaper
from bidi.algorithm import get_display
from django.http import HttpResponse
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from import_export import resources, fields
from .models import CustomUser
from django.core.mail import send_mail
from django.contrib import admin
from .models import UserSecondPassword  # اگر مسیرش فرق داره، اصلاح کن


class UserSecondPasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    readonly_fields = ('user',)

admin.site.register(UserSecondPassword, UserSecondPasswordAdmin)



class CustomUserResource(resources.ModelResource):
    username = fields.Field(column_name='نام کاربری', attribute='تام کاربری')
    phone = fields.Field(column_name='شماره همراه', attribute='phone')
    email = fields.Field(column_name='ایمیل', attribute='email')
    is_active = fields.Field(column_name='وضعیت فعال', attribute='is_active')
    is_staff = fields.Field(column_name='نوع کاربر', attribute='is_staff')
    date_joined = fields.Field(column_name='تاریخ عضویت', attribute='date_joined')

    class Meta:
        model = CustomUser
        fields = ('username', 'phone', 'email', 'is_active', 'is_staff', 'date_joined')
        export_order = ('username', 'phone', 'email', 'is_active', 'is_staff', 'date_joined')

    def dehydrate_is_active(self, user):
        return "فعال" if user.is_active else "غیرفعال"

    def dehydrate_is_staff(self, user):
        return "ادمین" if user.is_staff else "کاربر عادی"





def export_users_to_pdf(modeladmin, request, queryset):
    buffer = io.BytesIO()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=users.pdf'

    # ساخت canvas
    pdf = canvas.Canvas(buffer, pagesize=A4)
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Vazirmatn-Regular.ttf')
    pdfmetrics.registerFont(TTFont("Vazir", font_path))
    pdf.setFont("Vazir", 12)

    y = 800
    title = "لیست کاربران ثبت‌نام شده"
    reshaped_title = arabic_reshaper.reshape(title)
    bidi_title = get_display(reshaped_title)
    pdf.drawRightString(550, y, bidi_title)
    y -= 40

    for user in queryset:
        text = f"نام کاربری: {user.username} | ایمیل: {user.email or '-'} | شماره: {user.phone or '-'}"
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        pdf.drawRightString(550, y, bidi_text)
        y -= 25
        if y < 50:
            pdf.showPage()
            pdf.setFont("Vazir", 12)
            y = 800

    pdf.save()
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    return response

export_users_to_pdf.short_description = "📄 خروجی PDF فارسی"



# ✅ ادمین کاربر# from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

class CustomUserAdmin(ExportMixin, UserAdmin):
    resource_class = CustomUserResource

    model = CustomUser
    list_display = (
        'username',
        'is_active',
        'is_staff',
        'created_at',
        'updated_at',
    )


    readonly_fields = ('created_at', 'updated_at', 'slug')

    # اضافه کردن گروه‌ها و دسترسی‌ها به fieldsets:
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'phone', 'password')
        }),
        ('دسترسی‌ها', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('تاریخ‌ها و سیستم', {
            'fields': ('created_at', 'updated_at', 'slug'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)

    actions = [export_users_to_pdf]

# ثبت در پنل ادمین
admin.site.register(CustomUser, CustomUserAdmin)


class MassEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_at']
    actions = ['send_email_to_all']

    from django.core.mail import send_mail

    def send_email_to_all(self, request, queryset):
        # فرض می‌کنیم یک ایمیل از queryset گرفته می‌شود که موضوع و متن را دارد
        if not queryset.exists():
            self.message_user(request, "هیچ ایمیلی انتخاب نشده است.", level=messages.WARNING)
            return

        mass_email = queryset.first()

        subject = mass_email.subject
        html_message = mass_email.html_message  # اگر HTML داری
        from_email = settings.DEFAULT_FROM_EMAIL

        # لیست ایمیل‌های کاربران که ایمیل دارند
        recipients = list(CustomUser.objects.exclude(email='').values_list('email', flat=True))

        if not recipients:
            self.message_user(request, "هیچ کاربری با ایمیل معتبر یافت نشد.", level=messages.WARNING)
            return

        # ارسال ایمیل به هر کاربر به صورت جداگانه (برای شخصی‌سازی و اطمینان)
        success_count = 0
        for email in recipients:
            try:
                send_mail(
                    subject=subject,
                    message=html_message,  # اگر متن ساده است، بکار ببر، اگر HTML داری باید EmailMessage استفاده کنی
                    from_email=from_email,
                    recipient_list=[email],
                    fail_silently=False,
                )
                success_count += 1
            except Exception as e:
                # می‌توانی خطا را لاگ یا نمایش دهی
                pass

        self.message_user(request, f"{success_count} ایمیل با موفقیت ارسال شد.", level=messages.SUCCESS)


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


admin.site.register(MediaFile, MediaFileAdmin)