# D:\PROJECT\MIZAN_GOSTAR\PROJECT\SECTION\admin.py

import logging
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Section
from .forms import SectionAdminForm  # ایمپورت کردن فرم سفارشی

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = SectionAdminForm  # استفاده از فرم سفارشی برای ولیدیشن‌ها
    list_display = ['title', 'parent', 'get_level', 'order']  # نمایش level برای درک بهتر عمق
    list_filter = ['parent']
    search_fields = ['title']  # اضافه کردن قابلیت جستجو بر اساس عنوان

    def get_level(self, obj):
        """
        نمایش سطح سکشن در پنل ادمین.
        """
        level = obj.get_level()
        logger.debug(f"Admin is viewing section '{obj.title}' with level {level}.")
        return level

    get_level.short_description = "سطح"  # نام ستون در پنل ادمین

    def save_model(self, request, obj, form, change):
        """
        override save_model to add logging.
        """
        if change:
            logger.info(f"Admin '{request.user.username}' updated section '{obj.title}' (ID: {obj.pk}).")
        else:
            logger.info(f"Admin '{request.user.username}' added new section '{obj.title}'.")
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        override delete_model to add logging.
        """
        logger.warning(f"Admin '{request.user.username}' is deleting section '{obj.title}' (ID: {obj.pk}).")
        super().delete_model(request, obj)
