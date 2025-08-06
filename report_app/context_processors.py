from .models import Message
import sys

# تنظیم کدک خروجی به utf-8 برای جلوگیری از UnicodeEncodeError
sys.stdout.reconfigure(encoding='utf-8')

def unread_messages_count(request):
    """پردازنده محتوا برای اضافه کردن تعداد پیام‌های خوانده نشده به محتوای ادمین."""
    unread_count = 0
    if request.user.is_authenticated and request.user.is_superuser:
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        # دیباگ – نمایش در ترمینال
    return {'unread_messages_count': unread_count}