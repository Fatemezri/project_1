from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Comment
from .forms import CommentForm
from django.contrib import messages
from django.shortcuts import redirect




@login_required
def post_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            messages.success(request, "Your comment has been submitted for review. Thank you!")
            return redirect('some-redirect-url')  # Replace with a relevant URL
    else:
        form = CommentForm()

    return render(request, 'comments/post_comment.html', {'form': form})


