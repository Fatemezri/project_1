from .models import Message

def unread_messages_count(request):
    """پردازنده محتوا برای اضافه کردن تعداد پیام‌های خوانده نشده به محتوای ادمین."""
    unread_count = 0
    if request.user.is_authenticated and request.user.is_superuser:
        unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        # دستور اشکال‌زدایی: تعداد پیام‌های خوانده نشده را در کنسول نمایش می‌دهد.
        print(f"تعداد پیام‌های خوانده نشده برای سوپریوزر {request.user.username}: {unread_count}")
    return {'unread_messages_count': unread_count}