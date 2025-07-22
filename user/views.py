
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
                messages.error(request, 'کاربری با این مشخصات یافت نشد.')
                return redirect('login')

            if not check_password(password, user.password):
                messages.error(request, 'رمز عبور اشتباه است.')
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

            # اگر شماره باشد
            else:
                code = str(random.randint(100000, 999999))
                request.session['otp_code'] = code
                request.session['otp_user_id'] = user.id

                send_verification_sms(user.phone, code)

                messages.info(request, 'کد تایید به شماره شما ارسال شد.')
                return redirect('verify-phone')
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})





def send_login_link_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = generate_token(email)
            login_link = request.build_absolute_uri(
                reverse('confirm-login-link', args=[token])
            )
            send_mail(
                subject='لینک ورود به حساب',
                message=f'برای ورود به حساب خود روی لینک زیر کلیک کنید:\n{login_link}',
                from_email=None,
                recipient_list=[email],
            )
            return render(request, 'user/email_sent.html')
        except User.DoesNotExist:
            return render(request, 'user/send_link.html', {'error': 'ایمیل پیدا نشد.'})
    return render(request, 'user/send_link.html')

from .utils import verify_token

def confirm_login_link_view(request, token):
    email = verify_token(token)
    if not email:
        messages.error(request, 'لینک ورود منقضی شده یا نامعتبر است.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        login(request, user)
        messages.success(request, 'با موفقیت وارد شدید.')
        return redirect('home')  # یا هر جایی که صفحه اصلیته
    except CustomUser.DoesNotExist:
        messages.error(request, 'کاربر یافت نشد.')
        return redirect('login')


def password_reset_view(request, token):
    email = verify_token(token)
    if not email:
        return render(request, 'user/invalid_token.html')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return render(request, 'user/invalid_token.html')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            messages.success(request, "رمز عبور با موفقیت تغییر کرد.")
            return redirect('login')
    else:
        form = PasswordChangeForm()

    return render(request, 'user/password_reset.html', {'form': form})



def signin_view(request):
    if request.method == 'POST':
        form = signinForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data['password']

            user = CustomUser(username=username, email=email, phone=phone)
            user.set_password(password)
            user.save()
            if phone:
                send_verification_sms(phone, "ثبت‌نام شما با موفقیت انجام شد.")
            elif email:
                send_mail(
                    subject="ثبت‌نام موفق",
                    message="ثبت‌نام شما با موفقیت انجام شد.",
                    from_email="noreply@yourdomain.com",
                    recipient_list=[email],
                    fail_silently=True,
                )

            messages.success(request, 'ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.')
            return redirect('login')
    else:
        form = signinForm()

    return render(request, 'user/sign_in.html', {'form': form})



# اگر از مدل سفارشی User استفاده می‌کنی که رمز عبور رو هش می‌کنه (مثلاً با AbstractBaseUser یا AbstractUser)، هیچ‌وقت مستقیم password=form.cleaned_data['password'] نذار.
# باید از user.set_password() استفاده کنی که هش کنه.



def home(request):
    return render(request,'user/home.html')


# فرم درخواست بازیابی رمز عبور (شماره یا ایمیل)
def PasswordReset_email_view(request):
    if request.method == 'POST':
        form = passwordResetForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data['contact']
            try:
                if '@' in contact:
                    user = CustomUser.objects.get(email=contact)
                    token = generate_token(user.email)
                    reset_link = request.build_absolute_uri(reverse('password-reset', args=[token]))
                    send_mail(
                        subject='بازیابی رمز عبور',
                        message=f'برای تغییر رمز عبور روی لینک کلیک کنید:\n{reset_link}',
                        from_email='noreply@example.com',
                        recipient_list=[user.email]
                    )
                    messages.success(request, "لینک تغییر رمز به ایمیل شما ارسال شد.")
                    return redirect('login')
                else:
                    user = CustomUser.objects.get(phone=contact)
                    code = str(random.randint(100000, 999999))
                    request.session['reset_code'] = code
                    request.session['reset_phone'] = user.phone
                    send_verification_sms(user.phone, code)
                    return redirect('verify_reset_code')
            except CustomUser.DoesNotExist:
                messages.error(request, "کاربری با این اطلاعات پیدا نشد.")
    else:
        form = passwordResetForm()

    return render(request, 'user/passwordreset_email.html', {'form': form})




def forgot_password_view(request):
    if request.method == 'POST':
        form = passwordResetForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data['contact']

            try:
                if '@' in contact:
                    user = CustomUser.objects.get(email=contact)
                    token = generate_token(user.email)
                    verify_token(user.email, token)
                    messages.success(request, 'لینک بازیابی به ایمیل شما ارسال شد.')
                else:
                    user = CustomUser.objects.get(phone=contact)
                    send_verification_sms(user.phone, purpose='reset_password')
                    request.session['reset_phone'] = user.phone
                    return redirect('verify_reset_code')  # صفحه وارد کردن کد

            except CustomUser.DoesNotExist:
                messages.error(request, 'کاربری با این اطلاعات پیدا نشد.')
    else:
        form = passwordResetForm()

    return render(request, 'user/forgot_password.html', {'form': form})


def user_profile_view(request, slug):
    user = get_object_or_404(CustomUser, slug=slug)
    return render(request, 'user/profile.html', {'user_profile': user})



def password_reset_link_view(request, token):
    email = verify_token(token)
    if not email:
        messages.error(request, 'لینک نامعتبر یا منقضی شده است.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        messages.error(request, "کاربری با این ایمیل یافت نشد.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()
            messages.success(request, 'رمز عبور با موفقیت تغییر یافت.')
            return redirect('login')
    else:
        form = PasswordChangeForm()

    return render(request, 'user/password_reset.html', {'form': form})



def verify_phone_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        otp_code = request.session.get('otp_code')
        user_id = request.session.get('otp_user_id')

        if not (code and otp_code and user_id):
            messages.error(request, 'اطلاعات ناقص است. لطفاً دوباره تلاش کنید.')
            return redirect('login')

        if code == otp_code:
            try:
                user = User.objects.get(id=user_id)
                login(request, user)

                # پاک‌سازی امن session
                request.session.pop('otp_code', None)
                request.session.pop('otp_user_id', None)

                messages.success(request, f'{user.username} عزیز خوش آمدید!')
                return redirect('home')
            except User.DoesNotExist:
                messages.error(request, 'کاربر یافت نشد.')
        else:
            messages.error(request, 'کد وارد شده اشتباه است.')

    return render(request, 'user/verify_phone.html')
