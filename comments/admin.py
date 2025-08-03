from django.contrib import admin
from .models import Comment, Notification


@admin.register(Comment)
class CommentSuperuserAdmin(admin.ModelAdmin):
    """
    پنل مدیریت استاندارد برای سوپریوزرها با دسترسی کامل به ویرایش.
    """
    list_display = ('user', 'created_at', 'status', 'moderator_report')
    list_filter = ('status',)
    search_fields = ('user__username', 'text')
    actions = ['approve_selected']

    fields = ('user', 'text', 'status', 'moderator_report')
    readonly_fields = ('user', 'text')

    @admin.action(description='تایید نظرات انتخاب شده')
    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} نظر تایید شد.")


@admin.register(Notification)
class NotificationSuperuserAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'message', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('message', 'recipient__username', 'sender__username')
    readonly_fields = ('recipient', 'sender', 'message', 'related_comment')
    actions = ['mark_as_read']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='اعلان‌های انتخاب شده را به عنوان خوانده شده علامت‌گذاری کن')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} اعلان به عنوان خوانده شده علامت‌گذاری شدند.")