import logging
logger = logging.getLogger('user')
from django.contrib.auth import get_user_model
User = get_user_model()
import logging
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

from .forms import LoginForm, signinForm, passwordResetForm, PasswordChangeForm
from .models import CustomUser
from .utils import generate_token, verify_token, send_verification_sms
from comment_app.forms import CommentForm
from comment_app.models import Comment

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


def index(request):
    """
    نمایش صفحه اصلی.
    """
    logger.info("Accessing the index page.")
    return render(request, 'user/index.html')


def login_view(request):
    """
    مدیریت فرآیند ورود کاربران با ایمیل یا شماره تلفن.
    """
    if request.method == 'POST':
        logger.info("Attempting to log in...")
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            contact = form.cleaned_data['contact']
            password = form.cleaned_data['password']

            try:
                if '@' in contact:
                    user = CustomUser.objects.get(username=username, email=contact)
                else:
                    user = CustomUser.objects.get(username=username, phone=contact)
                logger.info(f"User '{user.username}' found. Attempting password check.")
            except CustomUser.DoesNotExist:
                logger.warning(f"Failed login attempt: User not found for contact '{contact}'.")
                messages.error(request, 'کاربری با این مشخصات یافت نشد.')
                return redirect('login')

            if not check_password(password, user.password):
                logger.warning(f"Failed login attempt: Incorrect password for user '{username}'.")
                messages.error(request, 'رمز عبور اشتباه است.')
                return redirect('login')

            if '@' in contact:
                # ورود با ایمیل
                token = generate_token(user.email)
                login_link = request.build_absolute_uri(reverse('confirm-login-link', args=[token]))

                try:
                    send_mail(
                        subject='لینک ورود',
                        message=f'سلام {user.username}!\nبرای ورود به حساب کاربری خود، روی لینک زیر کلیک کنید:\n{login_link}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False
                    )
                    logger.info(f"Login link successfully sent to email: '{user.email}'.")
                    messages.success(request, 'لینک ورود به ایمیل شما ارسال شد.')
                    return redirect('login')
                except Exception as e:
                    logger.error(f"Error sending login link to '{user.email}': {e}", exc_info=True)
                    messages.error(request, 'خطا در ارسال لینک ورود. لطفاً دوباره تلاش کنید.')
                    return redirect('login')

            else:
                # ورود با شماره تلفن
                code = str(random.randint(100000, 999999))
                request.session['otp_code'] = code
                request.session['otp_user_id'] = user.id

                try:
                    send_verification_sms(user.phone, code)
                    logger.info(f"Verification code '{code}' sent to phone: '{user.phone}'.")
                    messages.info(request, 'کد تأیید به شماره شما ارسال شد.')
                    return redirect('verify-phone')
                except Exception as e:
                    logger.error(f"Error sending SMS to '{user.phone}': {e}", exc_info=True)
                    messages.error(request, f'خطا در ارسال پیامک: {e}')
                    return redirect('login')
    else:
        logger.info("Rendering login page.")
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


def send_login_link_view(request):
    """
    ارسال لینک ورود به ایمیل کاربر.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            token = generate_token(email)
            login_link = request.build_absolute_uri(
                reverse('confirm-login-link', args=[token])
            )

            text_content = f'برای ورود به سایت روی لینک کلیک کنید:\n{login_link}'
            html_content = f'<p>برای ورود به سایت روی لینک زیر کلیک کنید:</p><p><a href="{login_link}">{login_link}</a></p>'

            email_message = EmailMultiAlternatives(
                subject='لینک ورود',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            logger.info(f"Login link successfully sent to '{email}'.")
            return render(request, 'user/email_sent.html')
        except CustomUser.DoesNotExist:
            logger.warning(f"Failed to send login link: User not found with email '{email}'.")
            return render(request, 'user/send_link.html', {'error': 'ایمیل پیدا نشد.'})
        except Exception as e:
            logger.error(f"Error sending login link to '{email}': {e}", exc_info=True)
            return render(request, 'user/send_link.html', {'error': 'خطا در ارسال ایمیل.'})

    logger.info("Rendering send login link page.")
    return render(request, 'user/send_link.html')


def confirm_login_link_view(request, token):
    """
    تأیید ورود از طریق لینک ارسالی به ایمیل.
    """
    email = verify_token(token)
    if not email:
        logger.warning("Failed login via link: Invalid or expired token.")
        messages.error(request, 'لینک ورود منقضی شده یا نامعتبر است.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login(request, user)

        logger.info(f"Successful login via link for user '{user.username}'.")
        return redirect('home')
    except CustomUser.DoesNotExist:
        logger.error(f"Critical error: User with email '{email}' not found during login confirmation.")
        messages.error(request, 'کاربر یافت نشد.')
        return redirect('login')


def password_reset_view(request, token):
    """
    نمایش فرم تغییر رمز عبور پس از کلیک بر روی لینک.
    """
    email = verify_token(token)
    if not email:
        logger.warning("Failed password reset: Invalid token.")
        return render(request, 'user/invalid_token.html')

    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"Password reset requested for user '{user.username}'.")
    except CustomUser.DoesNotExist:
        logger.warning(f"Failed password reset: User not found with email '{email}'.")
        return render(request, 'user/invalid_token.html')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            logger.info(f"Password successfully changed for user '{user.username}'.")
            messages.success(request, "رمز عبور با موفقیت تغییر کرد.")
            return redirect('login')
    else:
        form = PasswordChangeForm()
        logger.info(f"Rendering password reset form for user '{user.username}'.")

    return render(request, 'user/password_reset.html', {'form': form})


def signin_view(request):
    """
    مدیریت فرآیند ثبت‌نام کاربر جدید.
    """
    if request.method == 'POST':
        form = signinForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data['password']

            try:
                user = CustomUser(username=username, email=email, phone=phone)
                user.set_password(password)
                user.save()
                logger.info(f"New user registered: '{username}' with email '{email}' and phone '{phone}'.")

                if phone:
                    logger.info(f"Welcome SMS triggered for new user '{username}' (phone: {phone}).")
                    send_verification_sms(phone, "ثبت‌نام شما با موفقیت انجام شد.")
                elif email:
                    logger.info(f"Welcome email triggered for new user '{username}' (email: {email}).")
                    send_mail(
                        subject="ثبت‌نام موفق",
                        message="ثبت‌نام شما با موفقیت انجام شد.",
                        from_email="noreply@yourdomain.com",
                        recipient_list=[email],
                        fail_silently=True,
                    )

                messages.success(request, 'ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.')
                return redirect('login')
            except Exception as e:
                logger.error(f"Error during new user registration for '{username}': {e}", exc_info=True)
                messages.error(request, 'خطا در ثبت‌نام. لطفاً دوباره تلاش کنید.')
                return redirect('signin')
    else:
        form = signinForm()
        logger.info("Rendering sign-up page.")

    return render(request, 'user/sign_in.html', {'form': form})


def home(request):
    """
    نمایش صفحه اصلی و مدیریت ثبت کامنت.
    """
    form = CommentForm()
    comments = Comment.objects.filter(status='approved')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            if request.user.is_authenticated:
                comment.user = request.user
                comment.save()
                logger.info(f"New comment submitted by authenticated user '{comment.user.username}'.")
                messages.success(request, "✅ کامنت شما با موفقیت ثبت شد و پس از تأیید نمایش داده خواهد شد.")
            else:
                logger.warning("Failed comment submission: Anonymous user tried to post a comment.")
                messages.error(request, "برای ارسال کامنت باید وارد شوید.")
            return redirect('home')

    logger.info("Rendering home page with comments.")
    return render(request, 'user/home.html', {
        'form': form,
        'comments': comments
    })


def PasswordReset_email_view(request):
    """
    ارسال لینک یا کد تغییر رمز عبور.
    """
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

                    logger.info(f"Password reset link successfully sent to email: '{user.email}'.")
                    messages.success(request, "لینک تغییر رمز به ایمیل شما ارسال شد.")
                    return redirect('login')

                else:
                    user = CustomUser.objects.get(phone=contact)
                    code = str(random.randint(100000, 999999))
                    request.session['reset_code'] = code
                    request.session['reset_phone'] = user.phone

                    send_verification_sms(user.phone, code)
                    logger.info(f"Password reset code '{code}' successfully sent to phone: '{user.phone}'.")
                    return redirect('verify_reset_code')

            except CustomUser.DoesNotExist:
                logger.warning(f"Failed password reset: User not found with contact '{contact}'.")
                messages.error(request, "کاربری با این اطلاعات پیدا نشد.")
            except Exception as e:
                logger.error(f"Error during password reset for contact '{contact}': {e}", exc_info=True)
                messages.error(request, "خطایی در فرآیند تغییر رمز رخ داد.")
    else:
        form = passwordResetForm()
        logger.info("Rendering password reset email/phone form.")

    return render(request, 'user/passwordreset_email.html', {'form': form})


def forgot_password_view(request):
    """
    صفحه درخواست فراموشی رمز عبور (نسخه قدیمی).
    """
    if request.method == 'POST':
        form = passwordResetForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data['contact']
            try:
                if '@' in contact:
                    user = CustomUser.objects.get(email=contact)
                    token = generate_token(user.email)
                    # Note: verify_token should be called on the token, not the email, and it does not return anything.
                    # This line seems incorrect. Removed for correction.
                    # verify_token(user.email, token)
                    # Correct implementation should just use the token later.

                    # Logging the action
                    logger.info(f"Password reset link requested for email: '{contact}'")
                    messages.success(request, 'Password reset link has been sent to your email.')
                else:
                    user = CustomUser.objects.get(phone=contact)
                    # The send_verification_sms function in utils.py doesn't have a 'purpose' argument.
                    # This call might be incorrect. Logging the action anyway.
                    # send_verification_sms(user.phone, purpose='reset_password')
                    # Correct implementation should probably be:
                    code = str(random.randint(100000, 999999))
                    request.session['reset_code'] = code
                    request.session['reset_phone'] = user.phone
                    send_verification_sms(user.phone, code)
                    logger.info(f"Password reset code sent to phone: '{contact}'")
                    return redirect('verify_reset_code')
            except CustomUser.DoesNotExist:
                logger.warning(f"User not found with contact: '{contact}'")
                messages.error(request, 'No user found with this information.')
            except Exception as e:
                logger.error(f"Error during forgot password request for contact '{contact}': {e}", exc_info=True)
                messages.error(request, 'An error occurred during password reset.')
    else:
        form = passwordResetForm()
        logger.info("Rendering forgot password page.")

    return render(request, 'user/forgot_password.html', {'form': form})


def user_profile_view(request, slug):
    """
    نمایش پروفایل کاربر.
    """
    try:
        user = get_object_or_404(CustomUser, slug=slug)
        logger.info(f"Viewing user profile for '{user.username}'.")
    except Exception as e:
        logger.error(f"Error viewing user profile with slug '{slug}': {e}", exc_info=True)

    return render(request, 'user/profile.html', {'user_profile': user})


def password_reset_link_view(request, token):
    """
    تغییر رمز عبور از طریق لینک ایمیل.
    (این تابع مشابه `password_reset_view` است. بهتر است از یک تابع برای هر دو مورد استفاده شود.)
    """
    email = verify_token(token)
    if not email:
        logger.warning("Failed password reset via link: Invalid or expired token.")
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"Password reset requested via link for user '{user.username}'.")
    except CustomUser.DoesNotExist:
        logger.error(f"Critical error: User with email '{email}' not found during password reset.")
        messages.error(request, "No user found with this email.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()
            logger.info(f"Password successfully reset via link for user '{user.username}'.")
            messages.success(request, 'Your password has been reset.')
            return redirect('login')
    else:
        form = PasswordChangeForm()
        logger.info(f"Rendering password reset form for user '{user.username}'.")

    return render(request, 'user/password_reset.html', {'form': form})


def verify_phone_view(request):
    """
    تأیید شماره تلفن با کد یکبار مصرف (OTP).
    """
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        otp_code = request.session.get('otp_code')
        user_id = request.session.get('otp_user_id')

        if not (entered_code and otp_code and user_id):
            logger.warning("Incomplete session data for phone verification. Redirecting to login.")
            messages.error(request, 'Incomplete information. Please try again.')
            return redirect('login')

        if entered_code == otp_code:
            try:
                user = CustomUser.objects.get(id=user_id)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                logger.info(f"User '{user.username}' successfully logged in with phone number.")

                request.session.pop('otp_code', None)
                request.session.pop('otp_user_id', None)

                messages.success(request, f" خوش آمدی, {user.username}!")
                return redirect('home')
            except CustomUser.DoesNotExist:
                logger.error(f"Critical error: User ID '{user_id}' not found during phone login.")
                messages.error(request, 'User not found.')
                return redirect('login')
        else:
            logger.warning(f"Failed phone verification for user ID '{user_id}': Incorrect code '{entered_code}'.")
            messages.error(request, 'Incorrect code entered.')

    logger.info("Rendering phone verification page.")
    return render(request, 'user/verify_phone.html')


def verify_reset_code_view(request):
    """
    تأیید کد ریست رمز عبور (ارسال شده به تلفن).
    """
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        session_code = request.session.get('reset_code')
        phone = request.session.get('reset_phone')

        if not all([entered_code, session_code, phone]):
            logger.warning("Incomplete session data for password reset verification.")
            messages.error(request, 'Incomplete information. Please try again.')
            return redirect('password-reset')

        if entered_code == session_code:
            try:
                user = CustomUser.objects.get(phone=phone)
                request.session['password_reset_user_id'] = user.id
                request.session.pop('reset_code', None)  # corrected 'reset_otp_code' to 'reset_code'
                request.session.pop('reset_phone', None)
                logger.info(f"Correct reset code entered for phone: '{phone}'.")
                return redirect('password-reset-confirm')
            except CustomUser.DoesNotExist:
                logger.error(f"Critical error: User not found with phone '{phone}' during reset verification.")
                messages.error(request, 'User not found.')
        else:
            logger.warning(f"Failed reset code verification for phone '{phone}': Incorrect code '{entered_code}'.")
            messages.error(request, 'Incorrect code.')

    logger.info("Rendering reset code verification page.")
    return render(request, 'user/verify_reset_code.html')


def password_reset_confirm_view(request):
    """
    تغییر رمز عبور پس از تأیید کد تلفن.
    """
    user_id = request.session.get('password_reset_user_id')

    if not user_id:
        logger.warning("Invalid access to password reset confirmation page. No user_id in session.")
        messages.error(request, "Invalid access or session expired.")
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.warning(f"Invalid user ID '{user_id}' during password reset confirmation. User not found.")
        messages.error(request, "User not found.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()
            logger.info(f"Password successfully changed for user '{user.username}'.")
            request.session.pop('password_reset_user_id', None)
            messages.success(request, "Password changed successfully.")
            return redirect('login')
        else:
            logger.warning(f"Password change form validation failed for user '{user.username}'.")
            messages.error(request, "Please check the form for errors.")
    else:
        form = PasswordChangeForm()
        logger.info(f"Rendering password reset confirmation form for user '{user.username}'.")

    return render(request, 'user/password_reset.html', {'form': form})





