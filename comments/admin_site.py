# comments/admin_site.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from .models import Comment, Report
from django.contrib.auth import get_user_model

User = get_user_model()


class ModeratorAdminSite(admin.AdminSite):
    """
    پنل مدیریت سفارشی برای ناظران.
    """
    site_header = 'پنل ناظر'
    site_title = 'پنل ناظر'
    index_title = 'به پنل ناظر خوش آمدید'
    site_url = '/'

    def has_permission(self, request: HttpRequest) -> bool:
        user = request.user
        if not user.is_active or not user.is_staff:
            return False

        if user.is_superuser:
            return False

        return user.has_perm('comments.can_moderate_comments')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pending-comments/', self.admin_view(self.pending_comments_view), name='pending_comments'),
            path('approve-comment/<int:comment_id>/', self.admin_view(self.approve_comment), name='approve_comment'),
            path('reject-comment/<int:comment_id>/', self.admin_view(self.reject_comment), name='reject_comment'),
            path('send-report/<int:comment_id>/', self.admin_view(self.send_report_view), name='send_report'),
            path('notifications/', self.admin_view(self.notifications_view), name='moderator_notifications'),
        ]
        return custom_urls + urls

    def pending_comments_view(self, request):
        pending_comments = Comment.objects.filter(status='pending')
        context = {
            'title': 'نظرات در انتظار',
            'comments': pending_comments,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request, 'comments/moderator_admin/pending_comments.html', context)

    def approve_comment(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.status = 'approved'
            comment.save(update_fields=['status'])
            messages.success(request, f"نظر از {comment.user.username} تایید شد.")
        except Comment.DoesNotExist:
            messages.error(request, "نظر مورد نظر پیدا نشد.")
        return redirect('moderator_admin:pending_comments')

    def reject_comment(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.status = 'rejected'
            comment.save(update_fields=['status'])
            messages.success(request, f"نظر از {comment.user.username} رد شد.")
        except Comment.DoesNotExist:
            messages.error(request, "نظر مورد نظر پیدا نشد.")
        return redirect('moderator_admin:pending_comments')

    def send_report_view(self, request, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            messages.error(request, "نظر مورد نظر پیدا نشد.")
            return redirect('moderator_admin:pending_comments')

        if request.method == 'POST':
            report_text = request.POST.get('moderator_report')
            if report_text:
                comment.moderator_report = report_text
                comment.status = 'approved'
                comment.save(update_fields=['moderator_report', 'status'])
                messages.success(request, "گزارش ارسال و نظر تایید شد.")
            else:
                messages.error(request, "گزارش نمی‌تواند خالی باشد.")
            return redirect('moderator_admin:pending_comments')

        context = {
            'title': 'ارسال گزارش به سوپریوزر',
            'comment': comment,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request, 'comments/moderator_admin/send_report.html', context)

    def notifications_view(self, request):
        reports = Report.objects.filter(recipient=request.user, is_read=False)
        context = {
            'title': 'اعلانات ناظر',
            'notifications': reports,
            'notifications_list': reports,
        }
        return TemplateResponse(request, 'comments/moderator_admin/notifications.html', context)


moderator_admin_site = ModeratorAdminSite(name='moderator_admin')


@admin.register(Comment, site=moderator_admin_site)
class CommentModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status', 'view_actions')
    list_filter = ('status',)
    search_fields = ('user__username', 'text')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status__in=['pending', 'approved'])

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('comments.can_moderate_comments')

    def has_delete_permission(self, request, obj=None):
        return False

    def view_actions(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('moderator_admin:approve_comment', args=[obj.id])
            reject_url = reverse('moderator_admin:reject_comment', args=[obj.id])
            report_url = reverse('moderator_admin:send_report', args=[obj.id])

            return mark_safe(f"""
                <a href="{approve_url}" class="button button-approve">تایید</a>
                <a href="{reject_url}" class="button button-reject">رد</a>
                <a href="{report_url}" class="button button-report">گزارش</a>
            """)
        return ""

    view_actions.short_description = "اقدامات"


@admin.register(Report, site=moderator_admin_site)
class ReportModeratorAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'is_read')
    list_filter = ('is_read', 'report_type')
    search_fields = ('message',)
    actions = ['mark_as_read']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='انتخاب شده‌ها را به عنوان خوانده شده علامت‌گذاری کن')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} گزارش به عنوان خوانده شده علامت‌گذاری شدند.")