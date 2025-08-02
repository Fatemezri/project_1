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


class ModeratorAdminSite(admin.AdminSite):
    site_header = _('پنل ناظران')
    site_title = _('پنل ناظران')
    index_title = _('خوش آمدید به پنل ناظران')

    def has_permission(self, request: HttpRequest) -> bool:
        """
        Allow access only if the user is active, staff, and has permission to add, change,
        or view Comment model.
        """
        user = request.user
        if not (user.is_active and user.is_staff):
            return False

        # Check if user has any of the comment-related permissions
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
        """Custom view for pending comments."""
        pending_comments = Comment.objects.filter(status='pending')
        context = {
            'title': 'Pending Comments',
            'comments': pending_comments,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request, 'comments/moderator_admin/pending_comments.html', context)

    def approve_comment(self, request, comment_id):
        """Approve a comment and redirect."""
        comment = Comment.objects.get(pk=comment_id)
        if request.method == 'POST':
            comment.status = 'approved'
            comment.save(update_fields=['status'])
            messages.success(request, f"Comment from {comment.user.username} has been approved.")
        return redirect('moderator_admin:pending_comments')

    def reject_comment(self, request, comment_id):
        """Reject a comment and redirect."""
        comment = Comment.objects.get(pk=comment_id)
        if request.method == 'POST':
            comment.status = 'rejected'
            comment.save(update_fields=['status'])
            messages.success(request, f"Comment from {comment.user.username} has been rejected.")
        return redirect('moderator_admin:pending_comments')

    def send_report_view(self, request, comment_id):
        """Form for moderators to write a report."""
        comment = Comment.objects.get(pk=comment_id)
        if request.method == 'POST':
            report_text = request.POST.get('moderator_report')
            if report_text:
                comment.moderator_report = report_text
                comment.status = 'approved'  # Approve when report is sent
                comment.save(update_fields=['moderator_report', 'status'])
                messages.success(request, "Report sent and comment approved.")
                return redirect('moderator_admin:pending_comments')
            else:
                messages.error(request, "Report cannot be empty.")

        context = {
            'title': 'Send Report to Superuser',
            'comment': comment,
            'has_permission': self.has_permission(request),
        }
        return TemplateResponse(request, 'comments/moderator_admin/send_report.html', context)

    def notifications_view(self, request):
        """
        Custom view to show notifications for the moderator.
        """
        notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        context = {
            'title': 'Moderator Notifications',
            'notifications': notifications,
            'notifications_list': notifications,
        }
        return TemplateResponse(request, 'comments/moderator_admin/notifications.html', context)


# Instantiate the custom admin site
moderator_admin_site = ModeratorAdminSite(name='moderator_admin')


# Register models with the custom admin site
@admin.register(Comment, site=moderator_admin_site)
class CommentModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status', 'view_actions')
    list_filter = ('status',)
    search_fields = ('user__username', 'text')

    def get_queryset(self, request):
        # Moderators only see pending and approved comments
        qs = super().get_queryset(request)
        return qs.filter(status__in=['pending', 'approved'])

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('comments.can_moderate_comments')

    def has_delete_permission(self, request, obj=None):
        return False

    def view_actions(self, obj):
        """Custom column for moderation actions."""
        if obj.status == 'pending':
            return mark_safe(f"""
                <a href="{moderator_admin_site.reverse('approve_comment', args=[obj.id])}" class="button">Approve</a>
                <a href="{moderator_admin_site.reverse('reject_comment', args=[obj.id])}" class="button">Reject</a>
                <a href="{moderator_admin_site.reverse('send_report', args=[obj.id])}" class="button">Report</a>
            """)
        return ""

    view_actions.short_description = "Actions"
    view_actions.allow_tags = True


# Register the Notification model with the moderator admin site
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

    @admin.action(description='Mark selected notifications as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications were marked as read.")

