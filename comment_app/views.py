# D:\PROJECT\MIZAN_GOSTAR\PROJECT\COMMENT\views.py

import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentForm
from .models import Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# دریافت مدل کاربر
User = get_user_model()

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


def is_message_admin(user):
    """تابع کمکی برای بررسی اینکه آیا کاربر مدیر پیام است یا خیر."""
    logger.debug(f"Checking if user '{user.username}' is a MessageAdmin.")
    is_admin = user.groups.filter(name='MessageAdmins').exists()
    if is_admin:
        logger.info(f"User '{user.username}' is a MessageAdmin.")
    return is_admin


@login_required
def submit_comment(request):
    """نمایش برای کاربران جهت ثبت کامنت."""
    logger.info(f"User '{request.user.username}' is accessing the comment submission page.")
    if request.method == 'POST':
        logger.info(f"User '{request.user.username}' submitted a comment form.")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user

            if is_message_admin(request.user):
                comment.is_approved = True
                logger.info(f"Comment from admin '{request.user.username}' is auto-approved.")
            else:
                logger.info(f"Comment from user '{request.user.username}' is pending approval.")

            try:
                comment.save()
                logger.info(f"✅ Comment from user '{request.user.username}' saved successfully.")
                messages.success(request, "کامنت شما با موفقیت ثبت شد و پس از تایید نمایش داده خواهد شد.")
                return redirect('comment_success')
            except Exception as e:
                logger.error(f"❌ Error saving comment from user '{request.user.username}': {e}", exc_info=True)
                messages.error(request, "خطایی در هنگام ثبت کامنت رخ داد.")
                return render(request, 'comment_app/comment_form.html', {'form': form})
        else:
            logger.warning(f"❌ Comment form submitted by '{request.user.username}' is not valid. Errors: {form.errors}")
            return render(request, 'comment_app/comment_form.html', {'form': form})
    else:
        form = CommentForm()
        return render(request, 'comment_app/comment_form.html', {'form': form})


@login_required
def comment_success(request):
    """نمایش ساده برای نمایش پیام موفقیت پس از ثبت کامنت."""
    logger.info(f"User '{request.user.username}' is redirected to the comment success page.")
    return render(request, 'comment_app/comment_success.html')


def comment_list(request):
    """نمایش لیست کامنت‌های تایید شده برای همه کاربران."""
    logger.info("Accessing the public comment list page.")
    approved_comments = Comment.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'comment_app/comment_list.html', {'comments': approved_comments})