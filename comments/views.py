from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import Comment, Notification
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render
from .models import Comment

def comment_list(request):
    approved_comments = Comment.objects.filter(status='approved').order_by('-created_at')
    return render(request, 'comments/comment_list.html', {'comments': approved_comments})





from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Comment
from django.contrib.auth import get_user_model
from .models import Notification  # فرض بر اینه که این مدل داری

User = get_user_model()

@login_required
def submit_comment(request):
    if request.method == 'POST':
        text = request.POST.get('content')
        if text:
            comment = Comment.objects.create(user=request.user, content=text)

            moderator = User.objects.filter(groups__name='Moderators', is_active=True).first()
            if moderator:
                Notification.objects.create(
                    recipient=moderator,
                    sender=request.user,
                    notification_type='new_comment',
                    message=f"یک نظر جدید از طرف {request.user.username} ثبت شد.",
                    related_comment=comment
                )
            messages.success(request, "نظر شما ثبت شد و پس از بررسی منتشر خواهد شد.")
            return redirect('home')  # یا هر صفحه‌ای که میخوای بعد از ثبت هدایت بشه
        else:
            messages.error(request, "متن نظر نمی‌تواند خالی باشد.")

    return render(request, 'comment/submit.html')
