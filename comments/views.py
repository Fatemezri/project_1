from django.shortcuts import render, redirect
from .models import Comment
from .forms import CommentForm
from notifications.models import Notification
from django.contrib.auth.models import User

def add_comment(request):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()

            # ارسال اطلاعیه به مدیر
            managers = User.objects.filter(is_staff=True)
            for manager in managers:
                # Notification.objects.create(
                    user=manager,
                    message=f"نظر جدیدی از طرف {request.user.username} ثبت شده است."
                # )
            return redirect("comment_success")
    else:
        form = CommentForm()
    return render(request, "templates/comments/add_comment.html", {"form": form})




def submit_comment(request):
    if request.method == 'POST':
        Comment.objects.create(user=request.user, content=request.POST['content'])
        return redirect('user_panel')
    return render(request, 'user_panel.html')


def admin_panel(request):
    if not request.user.is_admin_user:
        return redirect('user_panel')
    comments = Comment.objects.all()
    return render(request, 'admin_panel.html', {'comments': comments})


def approve_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    comment.approved = True
    comment.save()


    senior_users = CustomUser.objects.filter(is_senior=True)
    for senior in senior_users:
        Notification.objects.create(
            user=senior,
            message=f"Comment from {comment.user.username} approved by admin."
        )
    return redirect('admin_panel')


def approve_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if request.user.is_staff:
        comment.approved = True
        comment.save()


        superusers = User.objects.filter(is_superuser=True)
        for su in superusers:
            Notification.objects.create(
                user=su,
                message=f"نظر تأیید شده توسط مدیر: {comment.text[:30]}"
            )
    return redirect("manager_dashboard")
