from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Section
from .forms import SectionAdminForm # ایمپورت کردن فرم سفارشی

@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = SectionAdminForm # استفاده از فرم سفارشی برای ولیدیشن‌ها
    list_display = ['title', 'parent', 'get_level', 'order'] # نمایش level برای درک بهتر عمق
    list_filter = ['parent']
    search_fields = ['title'] # اضافه کردن قابلیت جستجو بر اساس عنوان

    def get_level(self, obj):
        return obj.get_level()
    get_level.short_description = "سطح" # نام ستون در پنل ادمین