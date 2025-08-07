from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CommentForm
from .models import Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()
import logging
logger = logging.getLogger('comment')

def is_message_admin(user):
    """تابع کمکی برای بررسی اینکه آیا کاربر مدیر پیام است یا خیر."""
    return user.groups.filter(name='MessageAdmins').exists()

@login_required
def submit_comment(request):
    """نمایش برای کاربران جهت ثبت کامنت."""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            if is_message_admin(request.user):
                comment.is_approved = True
            comment.save()
            logger.info(
                f"New comment submitted by user: {request.user.username} | Approved: {comment.is_approved} | Content: {comment.text[:50]}"
            )

            return redirect('comment_success')
    else:
        form = CommentForm()
    return render(request, 'comment_app/comment_form.html', {'form': form})

@login_required
def comment_success(request):
    """نمایش ساده برای نمایش پیام موفقیت پس از ثبت کامنت."""
    return render(request, 'comment_app/comment_success.html')