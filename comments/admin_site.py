from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from .models import Comment, Notification
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class ModeratorAdminSite(admin.AdminSite):
    site_header = _('پنل ناظران')
    site_title = _('پنل ناظران')
    index_title = _('به پنل مدیریت ناظران خوش آمدید')

    def has_permission(self, request: HttpRequest) -> bool:
        user = request.user
        if not (user.is_active and user.is_staff):
            return False

        return (
            user.has_perm('comments.add_comment') or
            user.has_perm('comments.change_comment') or
            user.has_perm('comments.view_comment')
        )

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
            'title': 'نظرات در انتظار بررسی',
            'comments': pending_comments,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request, 'comments/moderator_admin/send_report.html', context)

    def approve_comment(self, request, comment_id):
        comment = Comment.objects.get(pk=comment_id)
        if request.method == 'POST':
            comment.status = 'approved'
            comment.save(update_fields=['status'])
            messages.success(request, f"نظر کاربر «{comment.user.username}» با موفقیت تأیید شد.")
        return redirect('moderator_admin:pending_comments')

    def reject_comment(self, request, comment_id):
        comment = Comment.objects.get(pk=comment_id)
        if request.method == 'POST':
            comment.status = 'rejected'
            comment.save(update_fields=['status'])
            messages.success(request, f"نظر کاربر «{comment.user.username}» با موفقیت رد شد.")
        return redirect('moderator_admin:pending_comments')

    def send_report_view(self, request, comment_id):
        comment = Comment.objects.get(pk=comment_id)
        if request.method == 'POST':
            report_text = request.POST.get('moderator_report')
            if report_text:
                comment.moderator_report = report_text
                comment.status = 'approved'
                comment.save(update_fields=['moderator_report', 'status'])
                messages.success(request, "گزارش با موفقیت ارسال شد و نظر تأیید گردید.")
                return redirect('moderator_admin:pending_comments')
            else:
                messages.error(request, "لطفاً متن گزارش را وارد کنید. این فیلد نمی‌تواند خالی باشد.")

        context = {
            'title': 'ارسال گزارش برای مدیر ارشد',
            'comment': comment,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request, 'comments/templates/comments/moderator_admin/send_report.html', context)

    def notifications_view(self, request):
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        context = {
            'title': 'اعلان‌های شما',
            'notifications': notifications,
            'notifications_list': notifications,
        }
        return TemplateResponse(request, 'comments/moderator_admin/notifications.html', context)


moderator_admin_site = ModeratorAdminSite(name='moderator_admin')


@admin.register(Comment, site=moderator_admin_site)
class CommentModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status', 'view_actions')
    list_filter = ('status',)
    search_fields = ('user__username', 'text')
    ordering = ('-created_at',)

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
                <a href="{approve_url}" class="button">تأیید</a>
                <a href="{reject_url}" class="button">رد</a>
                <a href="{report_url}" class="button">گزارش</a>
            """)
        return ""

    view_actions.short_description = "عملیات"
    view_actions.allow_tags = True


@admin.register(Notification, site=moderator_admin_site)
class NotificationModeratorAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'is_read')
    list_filter = ('is_read', 'notification_type')
    search_fields = ('message',)
    actions = ['mark_as_read']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='علامت‌گذاری به عنوان خوانده‌شده')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} اعلان به عنوان خوانده‌شده علامت‌گذاری شد.")
