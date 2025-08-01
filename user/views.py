

import logging
logger = logging.getLogger('user')
from .forms import signinForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.hashers import check_password
from .forms import LoginForm
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from .forms import passwordResetForm
from .utils import generate_token,  send_verification_sms
import random
from .forms import PasswordChangeForm
from django.shortcuts import render, redirect
from .models import CustomUser
from .utils import verify_token
from django.conf import settings
from django.contrib.auth import login
from comments.forms import CommentForm
from comments.models import Comment
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives





def index(request):
    return render(request, 'user/index.html')


def login_view(request):
    if request.method == 'POST':
        logger.info("📥 Login form submitted.")
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
                    logger.info(f"👤 User found: {user.username}")
            except User.DoesNotExist:
                logger.warning(f"❌ No user found with contact: {contact}")
                messages.error(request, 'کاربری با این مشخصات یافت نشد.')
                return redirect('login')

            if not check_password(password, user.password):
                logger.warning(f"🔑 Incorrect password for user {username}")
                messages.error(request, 'رمز عبور اشتباه است.')
                return redirect('login')

            if '@' in contact:
                token = generate_token(user.email)
                login_link = request.build_absolute_uri(reverse('confirm-login-link', args=[token]))

                send_mail(
                    subject='لینک ورود',
                    message=f'سلام {user.username}!\nبرای ورود به حساب کاربری خود، روی لینک زیر کلیک کنید:\n{login_link}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )

                logger.info(f"📧 Login link sent to email: {user.email}")
                messages.success(request, 'لینک ورود به ایمیل شما ارسال شد.')
                return redirect('login')

            else:
                code = str(random.randint(100000, 999999))
                request.session['otp_code'] = code
                request.session['otp_user_id'] = user.id
                logger.info(f"📲 Verification code sent to phone: {user.phone}")

                try:
                    send_verification_sms(user.phone, code)
                    messages.info(request, 'کد تأیید به شماره شما ارسال شد.')
                    return redirect('verify-phone')
                except Exception as e:
                    messages.error(request, f'خطا در ارسال پیامک: {e}')
                    return redirect('login')
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

            text_content = f'برای ورود به سایت روی لینک کلیک کنید:\n{login_link}'
            html_content = f'<p>برای ورود به سایت روی لینک زیر کلیک کنید:</p><p><a href="{login_link}">{login_link}</a></p>'

            email = EmailMultiAlternatives(
                subject='لینک ورود',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"📧 Login link sent to {email}.")
            return render(request, 'user/email_sent.html')
        except User.DoesNotExist:
            logger.warning(f"❌ No user found with email: {email}")
            return render(request, 'user/send_link.html', {'error': 'ایمیل پیدا نشد.'})
    return render(request, 'user/send_link.html')


def confirm_login_link_view(request, token):
    email = verify_token(token)
    if not email:
        messages.error(request, 'لینک ورود منقضی شده یا نامعتبر است.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login(request, user)

        logger.info(f"✅ Successful login via link for {email}")
        return redirect('home')
    except CustomUser.DoesNotExist:
        logger.error(f"❌ User with email {email} not found.")
        messages.error(request, 'کاربر یافت نشد.')
        return redirect('login')
def password_reset_view(request, token):
    email = verify_token(token)
    if not email:
        logger.warning("❌ Invalid reset token.")
        return render(request, 'user/invalid_token.html')

    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"🔐 Password reset requested for {email}")
    except CustomUser.DoesNotExist:
        logger.warning(f"❌ No user found with email: {email}")
        return render(request, 'user/invalid_token.html')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            logger.info(f"✅ Password successfully changed for {email}")
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
            logger.info(f"🆕 New registration: {username}")

            user = CustomUser(username=username, email=email, phone=phone)
            user.set_password(password)
            user.save()

            if phone:
                logger.info(f"📲 Welcome SMS sent to {phone}")
                send_verification_sms(phone, "ثبت‌نام شما با موفقیت انجام شد.")
            elif email:
                logger.info(f"📧 Welcome email sent to {email}")
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

def home(request):
    form = CommentForm()
    comments = Comment.objects.filter(approved=True).order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            if request.user.is_authenticated:
                comment.user = request.user
            else:
                logger.warning("❌ Anonymous user tried to post a comment.")
                return redirect('login')
            comment.save()
            logger.info(f"✅ New comment submitted by {comment.user}")
            messages.success(request, "✅ کامنت شما با موفقیت ثبت شد و پس از تأیید نمایش داده خواهد شد.")
            return redirect('home')

    return render(request, 'user/home.html', {
        'form': form,
        'comments': comments
    })


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
                        subject='عنوان ایمیل',
                        message=f'برای تغییر رمز عبور روی لینک کلیک کنید:\n{reset_link}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False
                    )

                    logger.info(f"📧 Password reset link sent to {user.email}")
                    messages.success(request, "لینک تغییر رمز به ایمیل شما ارسال شد.")
                    return redirect('login')

                else:
                    user = CustomUser.objects.get(phone=contact)
                    code = str(random.randint(100000, 999999))
                    request.session['reset_code'] = code
                    request.session['reset_phone'] = user.phone

                    send_verification_sms(user.phone, code)
                    logger.info(f"📲 Password reset code sent to {user.phone}")
                    return redirect('verify_reset_code')

            except CustomUser.DoesNotExist:
                logger.warning(f"❌ No user found with contact: {contact}")
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
                    logger.info(f"Password reset link sent to email: {contact}")
                    messages.success(request, 'Password reset link has been sent to your email.')
                else:
                    user = CustomUser.objects.get(phone=contact)
                    send_verification_sms(user.phone, purpose='reset_password')
                    request.session['reset_phone'] = user.phone
                    logger.info(f"Password reset code sent to phone: {contact}")
                    return redirect('verify_reset_code')
            except CustomUser.DoesNotExist:
                logger.warning(f"User not found with contact: {contact}")
                messages.error(request, 'No user found with this information.')
    else:
        form = passwordResetForm()

    return render(request, 'user/forgot_password.html', {'form': form})


def user_profile_view(request, slug):
    logger.info(f"Viewing user profile: {slug}")
    user = get_object_or_404(CustomUser, slug=slug)
    return render(request, 'user/profile.html', {'user_profile': user})


def password_reset_link_view(request, token):
    email = verify_token(token)
    if not email:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"Password reset requested via link for: {email}")
    except CustomUser.DoesNotExist:
        logger.error(f"User not found with email: {email}")
        messages.error(request, "No user found with this email.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()
            logger.info(f"Password successfully reset for {email}")
            messages.success(request, 'Your password has been reset.')
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
            messages.error(request, 'Incomplete information. Please try again.')
            return redirect('login')

        if code == otp_code:
            try:
                user = User.objects.get(id=user_id)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                logger.info(f"User logged in with phone number: {user.phone}")

                request.session.pop('otp_code', None)
                request.session.pop('otp_user_id', None)

                messages.success(request, f" خوش آمدی, {user.username}!")
                return redirect('home')
            except User.DoesNotExist:
                logger.warning("User not found during phone login.")
                messages.error(request, 'User not found.')
        else:
            logger.warning("Incorrect verification code entered.")
            messages.error(request, 'Incorrect code entered.')

    return render(request, 'user/verify_phone.html')


def verify_reset_code_view(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        session_code = request.session.get('reset_code')
        phone = request.session.get('reset_phone')

        if not all([entered_code, session_code, phone]):
            messages.error(request, 'Incomplete information. Please try again.')
            return redirect('password-reset')

        if entered_code == session_code:
            try:
                user = User.objects.get(phone=phone)
                request.session['password_reset_user_id'] = user.id
                request.session.pop('reset_otp_code', None)
                request.session.pop('reset_phone', None)
                logger.info(f"Correct reset code entered for phone: {phone}")
                return redirect('password-reset-confirm')
            except User.DoesNotExist:
                logger.error(f"User not found with phone: {phone}")
                messages.error(request, 'User not found.')
        else:
            logger.warning("Incorrect reset code entered.")
            messages.error(request, 'Incorrect code.')

    return render(request, 'user/verify_reset_code.html')


def password_reset_confirm_view(request):
    user_id = request.session.get('password_reset_user_id')

    if not user_id:
        messages.error(request, "Invalid access or session expired.")
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.warning("Invalid user ID during password reset confirmation.")
        messages.error(request, "User not found.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()
            logger.info(f"Password successfully changed for user: {user.username}")
            request.session.pop('password_reset_user_id', None)
            messages.success(request, "Password changed successfully.")
            return redirect('login')
        else:
            messages.error(request, "Please check the form for errors.")
    else:
        form = PasswordChangeForm()

    return render(request, 'user/password_reset.html', {'form': form})




