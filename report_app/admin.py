from django.contrib import admin
from .models import Message
from .forms import MessageAdminForm
import logging
logger = logging.getLogger('report')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['sender__username', 'recipient__username', 'content']

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.is_superuser:
            kwargs['form'] = MessageAdminForm  # Custom form for moderators
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        # Moderators can't edit these fields
        if not request.user.is_superuser:
            return ['is_read', 'created_at']
        return ['created_at']

    def has_change_permission(self, request, obj=None):
        # Allow all users to mark messages as read, but restrict field access in the form
        return True
