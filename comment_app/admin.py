# D:\PROJECT\MIZAN_GOSTAR\PROJECT\COMMENT\admin.py

import logging
from django.contrib import admin, messages
from .models import Comment

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


# ثبت مدل کامنت در پنل ادمین
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        """
        اکشن ادمین برای تایید کامنت‌های انتخاب شده.
        """
        updated_count = queryset.update(is_approved=True)
        self.message_user(request, f"{updated_count} کامنت با موفقیت تایید شدند.")
        logger.info(f"✅ Admin '{request.user.username}' approved {updated_count} comments.")

    approve_comments.short_description = "تایید کامنت‌های انتخاب شده"

    def get_queryset(self, request):
        """
        فقط کامنت‌های تایید نشده را برای سوپریوزرها در پنل ادمین پیش‌فرض نمایش می‌دهد.
        """
        qs = super().get_queryset(request)
        logger.info(f"Admin '{request.user.username}' is accessing the Comment list.")

        if not request.user.is_superuser:
            logger.warning(
                f"Admin '{request.user.username}' attempted to access comments but is not a superuser. Access denied.")
            return qs.none()

        logger.debug(f"Superuser '{request.user.username}' is viewing comments.")
        return qs