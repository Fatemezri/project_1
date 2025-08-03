# comments/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from .models import Comment, Report

User = get_user_model()


class MyAdminSite(admin.AdminSite):
    """
    پنل مدیریت اصلی برای سوپریوزرها.
    """
    site_header = 'مدیریت وب‌گاه'
    site_title = 'پنل مدیریت'
    index_title = 'به پنل مدیریت خوش آمدید'

    def has_permission(self, request: HttpRequest) -> bool:
        # فقط سوپریوزرها می‌توانند به این پنل دسترسی داشته باشند
        return request.user.is_active and request.user.is_superuser

    def index(self, request, extra_context=None):
        if request.user.is_superuser:
            unread_reports_count = Report.objects.filter(
                recipient=request.user,
                is_read=False,
                report_type='moderator_report'
            ).count()

            if unread_reports_count > 0:
                notification_message = mark_safe(
                    f"شما <a href='{reverse('main_admin:comments_report_changelist')}'>{unread_reports_count} گزارش خوانده نشده</a> دارید."
                )
                messages.info(request, notification_message)

        return super().index(request, extra_context)

main_admin_site = MyAdminSite(name='main_admin')


@admin.register(Comment, site=main_admin_site)
class CommentMainAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'text')


@admin.register(Report, site=main_admin_site)
class ReportMainAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'is_read')
    list_filter = ('is_read', 'report_type')
    search_fields = ('message',)
    actions = ['mark_as_read']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(recipient=request.user)

    @admin.action(description='انتخاب شده‌ها را به عنوان خوانده شده علامت‌گذاری کن')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} گزارش به عنوان خوانده شده علامت‌گذاری شدند.")