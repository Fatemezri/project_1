from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import ModeratorReport

def is_moderator(user):
    return user.groups.filter(name='Moderators').exists()

@user_passes_test(is_moderator)
def submit_report(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        ModeratorReport.objects.create(moderator=request.user, content=content)
        # TODO: ارسال نوتیفیکیشن به سوپریوزر
        return redirect('moderator_panel')
    return render(request, 'report/submit.html')
