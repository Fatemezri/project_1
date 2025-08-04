import logging
from django.contrib import admin
from .models import Message

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


# ثبت مدل پیام در پنل ادمین
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'content', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'content')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        logger.info("MessageAdmin is registered in the admin panel.")
