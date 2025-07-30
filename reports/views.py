from django.shortcuts import render, redirect
from .models import Report
from .forms import ReportForm
from django.contrib.auth.models import User
from notifications.models import Notification

def send_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.manager = request.user
            report.save()


            superusers = User.objects.filter(is_superuser=True)
            for su in superusers:
                Notification.objects.create(
                    user=su,
                    message=f"گزارش جدید از {request.user.username}: {report.title}"
                )

            return redirect("report_success")
    else:
        form = ReportForm()

    return render(request, "templates/reports/send_report.html", {"form": form})
