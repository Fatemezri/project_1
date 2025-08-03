from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Comment
from django.contrib.auth.decorators import login_required


@login_required
def submit_comment(request):
    """
    View برای ثبت یک نظر جدید.
    """
    if request.method == 'POST':
        text = request.POST.get('comment_text')
        if text:
            Comment.objects.create(user=request.user, text=text)
            messages.success(request, "نظر شما با موفقیت ثبت شد و پس از بررسی منتشر خواهد شد.")
        else:
            messages.error(request, "متن نظر نمی‌تواند خالی باشد.")
    return redirect('some_other_view_or_homepage') # اینجا را با آدرس صفحه مورد نظر خود جایگزین کنید.

