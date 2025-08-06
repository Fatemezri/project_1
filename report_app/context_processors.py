from .models import Message

def unread_message_count(request):
    if request.user.is_authenticated and request.user.is_superuser:
        count = Message.objects.filter(is_read=False).count()
        return {'unread_count': count}
    return {}