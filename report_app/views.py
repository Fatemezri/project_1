from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()
import logging
logger = logging.getLogger('report')

@login_required
def superuser_messages(request):
    """نمایش برای سوپریوزرها جهت مشاهده پیام‌های داخلی خود."""
    if not request.user.is_superuser:
        logger.warning(f"Unauthorized access attempt by user {request.user.username} (ID: {request.user.id})")
        return HttpResponseForbidden("شما دسترسی لازم برای ورود به این صفحه را ندارید.")

    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')


    unread_messages = messages.filter(is_read=False)
    unread_messages.update(is_read=True)


    return render(request, 'report_app/superuser_messages.html', {'messages': messages})