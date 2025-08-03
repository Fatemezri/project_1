from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Comment, Report  # مدل Notification به Report تغییر نام یافته است.

User = get_user_model()


def comment_list(request):
    approved_comments = Comment.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'comments/comment_list.html', {'comments': approved_comments})


@login_required
def submit_comment(request):
    if request.method == 'POST':
        text = request.POST.get('comment_text')
        if text:
            comment = Comment.objects.create(user=request.user, text=text)

            # ارسال گزارش به اولین ناظر پیدا شده
            moderator = User.objects.filter(groups__name='Moderators', is_active=True).first()
            if moderator:
                Report.objects.create(  # نام مدل به Report تغییر یافته است
                    recipient=moderator,
                    sender=request.user,
                    report_type='new_comment',  # نوع گزارش را new_comment قرار می‌دهیم
                    message=f"یک نظر جدید از طرف {request.user.username} ثبت شد.",
                    related_comment=comment
                )

            messages.success(request, "نظر شما ثبت شد و پس از بررسی منتشر خواهد شد.")
        else:
            messages.error(request, "متن نظر نمی‌تواند خالی باشد.")

        # پس از ارسال موفقیت‌آمیز فرم، به یک صفحه دیگر هدایت شوید
        # نام view یا URL مورد نظر خود را جایگزین کنید
        return redirect('some_other_view_or_homepage')

    return render(request, 'comment/submit.html')