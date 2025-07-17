from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.core.mail import send_mail
from .utils import generate_token
from .forms import LoginForm, signForm
from django.contrib.auth import get_user_model, login

User = get_user_model()

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            contact = form.cleaned_data['contact']
            password = form.cleaned_data['password']


            try:
                if '@' in contact:
                    user = User.objects.get(username=username, email=contact)
                else:
                    user = User.objects.get(username=username, phone=contact)
            except User.DoesNotExist:
                messages.error(request, 'کاربر یافت نشد.')
                return redirect('login')


            if '@' in contact:
                token = generate_token(user.email)
                login_link = request.build_absolute_uri(reverse('confirm-login-link', args=[token]))

                send_mail(
                    'لینک ورود به حساب',
                    f'برای ورود روی این لینک کلیک کنید:\n{login_link}',
                    'noreply@example.com',  # یا settings.DEFAULT_FROM_EMAIL
                    [user.email]
                )

                messages.success(request, 'لینک ورود به ایمیل شما ارسال شد.')
                return redirect('login')


            else:
                #
                messages.info(request, 'کد تایید به شماره شما ارسال شد.')
                return redirect('verify-phone')  # صفحه ورود کد تأیید

    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


