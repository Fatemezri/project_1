from django.contrib import admin
from .models import Comment
from django.utils.html import format_html
import logging
logger = logging.getLogger('comment')



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_comments']
    readonly_fields = ('user',)
    fields = ('content', 'is_approved')

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "کامنت‌های انتخاب شده تایید شدند.")

        for comment in queryset:
            logger.info(f"Comment approved by {request.user.username}: {comment.id} by {comment.user.username}")

    approve_comments.short_description = "تایید کامنت‌های انتخاب شده"


    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name='MessageAdmins').exists()

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs  # Show all comments to moderators, approved and unapproved
        return qs

    def approval_status(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green;">✔ تایید شده</span>')
        return format_html('<span style="color: red;">✘ نیاز به تایید</span>')

    approval_status.short_description = 'وضعیت تایید'