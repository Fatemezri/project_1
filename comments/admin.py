from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from comments.models import Comment, Notification


class MyAdminSite(admin.AdminSite):
    """
    A custom admin site for the main superuser panel.
    """
    site_header = 'مدیریت وب‌گاه'
    site_title = 'پنل مدیریت'
    index_title = 'به پنل مدیریت خوش آمدید'

    def index(self, request, extra_context=None):
        # Check for unread notifications for the superuser
        if request.user.is_superuser:
            unread_notifications_count = Notification.objects.filter(
                recipient=request.user, is_read=False, notification_type='moderator_report'
            ).count()

            if unread_notifications_count > 0:
                # The HTML for the message, including a clickable link
                notification_message = mark_safe(
                    f"شما <a href='{reverse('admin:comments_notification_changelist')}'>{unread_notifications_count} گزارش خوانده نشده</a> دارید."
                )

                # Add the message to Django's messages framework
                messages.info(request, notification_message)

        # Call the original index view to render the page
        return super().index(request, extra_context)


main_admin_site = MyAdminSite(name='main_admin')


# Register your models with the custom main admin site
@admin.register(Comment, site=main_admin_site)
class CommentMainAdmin(admin.ModelAdmin):
    # ... your admin configuration for the main panel
    pass


@admin.register(Notification, site=main_admin_site)
class NotificationMainAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'is_read')
    list_filter = ('is_read', 'notification_type')
    actions = ['mark_as_read']

    def get_queryset(self, request):
        # Filter notifications to show only those for the current user
        qs = super().get_queryset(request)
        return qs.filter(recipient=request.user)

    @admin.action(description='انتخاب شده‌ها را به عنوان خوانده شده علامت‌گذاری کن')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} اعلان به عنوان خوانده شده علامت‌گذاری شدند.")