from django.contrib import admin
from django.contrib.auth.models import Group
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
    """
    یک پنل مدیریت سفارشی برای ناظران (moderators).
    """
    site_header = 'پنل ناظر'
    site_title = 'پنل ناظر'
    index_title = 'به پنل ناظر خوش آمدید'
    site_url = '/'

    def has_permission(self, request: HttpRequest) -> bool:
        user = request.user
        if not (user.is_active):
            return False

        if user.is_superuser:
            return False

        # Only grant access to users who have a specific moderator permission.
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
        """نمایش سفارشی برای نظرات در انتظار."""
        pending_comments = Comment.objects.filter(status='pending')
        context = {
            'title': 'نظرات در انتظار',
            'comments': pending_comments,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request,'comments/moderator_admin/pending_comments.html', context)

    def approve_comment(self, request, comment_id):
        """تایید یک نظر و ریدایرکت."""