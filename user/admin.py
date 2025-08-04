from django.contrib import  messages
from django.core.mail import EmailMessage
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
from django.contrib.auth.models import Group

import io
import os
import logging
import re
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.conf import settings
from django.utils.html import format_html
from django.utils.text import slugify
from import_export import resources, fields
from import_export.admin import ExportMixin
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# دریافت مدل‌های مرتبط
from .forms import MediaFileAdminForm
from .models import CustomUser, MassEmail, MediaFile
from .utils import delete_file_from_arvan, generate_presigned_url

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class CustomUserResource(resources.ModelResource):
    username = fields.Field(column_name='نام کاربری', attribute='username')
    phone = fields.Field(column_name='شماره همراه', attribute='phone')
    email = fields.Field(column_name='ایمیل', attribute='email')
    is_active = fields.Field(column_name='وضعیت فعال', attribute='is_active')
    is_staff = fields.Field(column_name='نوع کاربر', attribute='is_staff')
    date_joined = fields.Field(column_name='تاریخ عضویت', attribute='created_at')

    class Meta:
        model = CustomUser
        fields = ('username', 'phone', 'email', 'is_active', 'is_staff', 'created_at')
        export_order = ('username', 'phone', 'email', 'is_active', 'is_staff', 'created_at')

    def dehydrate_is_active(self, user):
        logger.debug(f"Dehydrating is_active for user '{user.username}'.")
        return "فعال" if user.is_active else "غیرفعال"

    def dehydrate_is_staff(self, user):
        logger.debug(f"Dehydrating is_staff for user '{user.username}'.")
        return "ادمین" if user.is_staff else "کاربر عادی"


def export_users_to_pdf(modeladmin, request, queryset):
    """
    اکشن ادمین برای خروجی گرفتن لیست کاربران در قالب PDF فارسی.
    """
    logger.info(f"Admin action 'export_users_to_pdf' started by user '{request.user.username}'.")
    try:
        buffer = io.BytesIO()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=users.pdf'

        # ساخت canvas
        pdf = pdf_canvas.Canvas(buffer, pagesize=A4)
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Vazirmatn-Regular.ttf')
        if not os.path.exists(font_path):
            logger.error(f"❌ PDF font file not found at {font_path}")
            messages.error(request, "فایل فونت برای ساخت PDF یافت نشد. لطفاً آن را در مسیر static/fonts قرار دهید.")
            return

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
        logger.info(f"✅ PDF export successful for {queryset.count()} users.")
        return response
    except Exception as e:
        logger.error(f"❌ Error exporting users to PDF: {e}", exc_info=True)
        messages.error(request, f"خطا در ساخت فایل PDF: {e}")


export_users_to_pdf.short_description = "📄 خروجی PDF فارسی"


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
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)

    actions = [export_users_to_pdf]


# ثبت در پنل ادمین
admin.site.register(CustomUser, CustomUserAdmin)


# admin.site.unregister(Group) # اگر می‌خواهید گروه‌ها را از پنل ادمین حذف کنید

class MassEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_at']
    actions = ['send_email_to_all']

    def send_email_to_all(self, request, queryset):
        """
        ارسال ایمیل از طریق اکشن ادمین.
        """
        logger.info(f"Admin action 'send_email_to_all' started by user '{request.user.username}'.")
        # این اکشن باید روی یک MassEmail اجرا شود، بنابراین فقط اولین آیتم را انتخاب می‌کنیم.
        if not queryset:
            messages.warning(request, "لطفاً حداقل یک ایمیل را برای ارسال انتخاب کنید.")
            logger.warning("Admin action 'send_email_to_all' called without a selected object.")
            return

        mass_email = queryset.first()
        subject = mass_email.subject
        html_message = mass_email.html_message
        from_email = settings.DEFAULT_FROM_EMAIL

        logger.info(f"Email subject is '{subject}'.")

        recipients = CustomUser.objects.exclude(email='').values_list('email', flat=True)
        if not recipients:
            messages.warning(request, "هیچ کاربری با ایمیل معتبر یافت نشد.")
            logger.warning("No active users with email found to send mass email.")
            return

        logger.info(f"Found {len(recipients)} recipients. Attempting to send email.")

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=[],
            bcc=recipients,
        )
        email.content_subtype = "html"

        try:
            email.send()
            messages.success(request, f"{len(recipients)} ایمیل با موفقیت ارسال شد.")
            logger.info(f"✅ Mass email successfully sent to {len(recipients)} users.")
        except Exception as e:
            messages.error(request, f"خطا در ارسال ایمیل: {str(e)}")
            logger.error(f"❌ Error sending mass email: {e}", exc_info=True)

    send_email_to_all.short_description = "ارسال ایمیل به همه کاربران"


admin.site.register(MassEmail, MassEmailAdmin)


class MediaFileAdmin(admin.ModelAdmin):
    form = MediaFileAdminForm
    list_display = ['file_link', 'is_minified', 'uploaded_at', 'download_link']
    readonly_fields = ['download_link']

    def file_link(self, obj):
        return obj.file.name

    file_link.short_description = "نام فایل"

    def download_link(self, obj):
        logger.info(f"Attempting to generate download link for file: '{obj.file.name}'.")
        if obj.file and obj.file.name:
            try:
                url = generate_presigned_url(obj.file.name)
                if url:
                    logger.info(f"✅ Presigned URL generated successfully for '{obj.file.name}'.")
                    return format_html(f"<a href='{url}' target='_blank'>دانلود</a>")
                else:
                    logger.warning(f"❌ Failed to generate presigned URL for '{obj.file.name}'.")
                    return "خطا در تولید لینک"
            except Exception as e:
                logger.error(f"❌ Unexpected error generating URL for '{obj.file.name}': {e}", exc_info=True)
                return "خطا در تولید لینک"
        logger.warning(f"File object for '{obj}' has no name. Cannot generate download link.")
        return "فایلی وجود ندارد"

    download_link.short_description = "دانلود فایل"

    def delete_model(self, request, obj):
        """
        حذف فایل از فضای ابری قبل از حذف مدل.
        """
        logger.info(f"Admin action 'delete_model' triggered for MediaFile with key '{obj.file.name}'.")
        try:
            delete_file_from_arvan(obj.file.name)
            logger.info(f"✅ File '{obj.file.name}' deleted from ArvanCloud.")
            super().delete_model(request, obj)
            logger.info(f"✅ MediaFile object deleted from database.")
        except Exception as e:
            logger.error(f"❌ Error deleting MediaFile '{obj.file.name}': {e}", exc_info=True)
            messages.error(request, f"خطا در حذف فایل: {str(e)}")

    def save_model(self, request, obj, form, change):
        """
        مدیریت ذخیره مدل. (فایل توسط فرم مدیریت می‌شود)
        """
        logger.debug(f"save_model called for MediaFile '{obj.file.name}'. Change: {change}.")
        super().save_model(request, obj, form, change)


admin.site.register(MediaFile, MediaFileAdmin)


