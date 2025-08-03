# comments/admin_site.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from .models import Comment, Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class ModeratorAdminSite(admin.AdminSite):
    site_header = 'پنل ناظر'
    site_title = 'پنل ناظر'
    index_title = 'به پنل ناظر خوش آمدید'
    site_url = '/'

    def has_permission(self, request: HttpRequest) -> bool:
        user = request.user
        if not user.is_active:
            return False

        # Check if the user is a staff member first (required for all admin sites)
        if not user.is_staff:
            return False

        # Superusers are explicitly denied, only moderators with the permission can access.
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
        # We will use GET requests to make this simple and avoid CSRF issues for now
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
                # Saving the model will now trigger the signal
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
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        context = {
            'title': 'اعلانات ناظر',
            'notifications': notifications,
            'notifications_list': notifications,
        }
        return TemplateResponse(request, 'comments/moderator_admin/notifications.html', context)


moderator_admin_site = ModeratorAdminSite(name='moderator_admin')