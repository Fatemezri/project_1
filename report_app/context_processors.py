import logging
from .models import Message

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)

def unread_messages_count(request):
    """پردازنده محتوا برای اضافه کردن تعداد پیام‌های خوانده نشده به محتوای ادمین."""
    logger.debug(f"Context processor 'unread_messages_count' called for user '{request.user.username}'.")
    unread_count = 0
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
            logger.info(f"Unread messages count for superuser '{request.user.username}': {unread_count}")
        except Exception as e:
            logger.error(f"❌ Error fetching unread message count for user '{request.user.username}': {e}", exc_info=True)
            # در صورت بروز خطا، برای جلوگیری از از کار افتادن برنامه، ۰ را برمی‌گردانیم.
            unread_count = 0
    else:
        logger.debug(f"User '{request.user.username}' is not a superuser or not authenticated. Returning count 0.")
    return {'unread_messages_count': unread_count}
