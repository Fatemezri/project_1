from django.shortcuts import render


from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from notifications.models import Notification

@user_passes_test(lambda u: u.is_staff)
def manager_dashboard(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, "dashboard/manager.html", {"notification": notifications})

@user_passes_test(lambda u: u.is_superuser)
def superuser_dashboard(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, "dashboard/superuser.html", {"notification": notifications})
