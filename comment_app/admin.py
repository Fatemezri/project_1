from django.contrib import admin
from .models import Comment


# ثبت مدل کامنت در پنل ادمین
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "کامنت‌های انتخاب شده تایید شدند.")

    approve_comments.short_description = "تایید کامنت‌های انتخاب شده"

    # فقط کامنت‌های تایید نشده را برای سوپریوزرها در پنل ادمین پیش‌فرض نمایش می‌دهد
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.none()  # سایر ادمین‌ها را از دیدن این موارد محدود می‌کند
        return qs
