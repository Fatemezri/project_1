from django.contrib import admin
from .models import Comment, Notification


# --- پنل مدیریت برای سوپریوزرها ---
@admin.register(Comment)
class CommentSuperuserAdmin(admin.ModelAdmin):
    """
    پنل مدیریت سوپریوزرها با دسترسی کامل برای مشاهده و ویرایش نظرات.
    """
    list_display = ('user', 'created_at', 'status', 'moderator_report')
    list_filter = ('status',)
    search_fields = ('user__username', 'text')
    actions = ['approve_selected']

    fields = ('user', 'text', 'status', 'moderator_report')
    readonly_fields = ('user',)

    @admin.action(description='تأیید نظرات انتخاب‌شده')
    def approve_selected(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} نظر با موفقیت تأیید شد.")


@admin.register(Notification)
class NotificationSuperuserAdmin(admin.ModelAdmin):
    """
    مدیریت اعلان‌ها توسط سوپریوزرها، فقط برای مشاهده و علامت‌گذاری به‌عنوان خوانده‌شده.
    """
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

    @admin.action(description='علامت‌گذاری اعلان‌های انتخاب‌شده به عنوان خوانده‌شده')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} اعلان با موفقیت به عنوان خوانده‌شده علامت‌گذاری شد.")
