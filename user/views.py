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
from comment_app.forms import CommentForm
from comment_app.models import Comment
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from .models import UserSecondPassword
import logging


logger = logging.getLogger('user')
def custom_simple_hash(password, salt='mysalt'):
    try:
        logger.info("🔐 Starting second password hashing.")
        hashed = ''
        for i, c in enumerate(password + salt):
            hashed += chr((ord(c) + i) % 126)
        result = hashed.encode('utf-8').hex()
        logger.info("✅ Second password hashed successfully.")
        return result
    except Exception as e:
        logger.error(f"❌ Error while hashing second password: {e}")
        raise

def index(request):
    return render(request, 'user/index.html')  # صفحه اصلی

logger = logging.getLogger('user')
def home(request):
    form = CommentForm()
    comments = Comment.objects.filter(is_approved=True)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            if not request.user.is_authenticated:
                logger.warning("❌ Anonymous user tried to post a comment.")
                messages.error(request, "برای ارسال نظر ابتدا وارد حساب خود شوید.")
                return redirect('login')

            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()

            logger.info(f"📝 New comment submitted by user '{comment.user.username}' (ID: {comment.user.id})")
            messages.success(request, "✅ کامنت شما با موفقیت ثبت شد و پس از تأیید نمایش داده خواهد شد.")
            return redirect('home')
        else:
            logger.warning("⚠️ Invalid comment form submitted.")

    return render(request, 'user/home.html', {
        'form': form,
        'comments': comments
    })


logger = logging.getLogger('user')
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
                    logger.info(f"👤 User found: {user.username} (ID: {user.id})")
            except User.DoesNotExist:
                logger.warning(f"❌ No user found with contact: {contact}")
                messages.error(request, 'کاربری با این مشخصات یافت نشد.')
                return redirect('login')

            if not check_password(password, user.password):
                logger.warning(f"🔑 Incorrect password attempt for user '{username}'")
                messages.error(request, 'رمز عبور اشتباه است.')
                return redirect('login')

            if '@' in contact:
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
                    logger.info(f"📧 Login token sent to {user.email}")
                except Exception as e:
                    logger.error(f"📧 Failed to send login email to {user.email} - {e}")
                    messages.error(request, 'خطا در ارسال ایمیل.')
                    return redirect('login')

                messages.success(request, 'لینک ورود به ایمیل شما ارسال شد.')
                return redirect('login')

            else:
                code = str(random.randint(100000, 999999))
                request.session['otp_code'] = code
                request.session['otp_user_id'] = user.id
                logger.info(f"📲 SMS verification code sent to {user.phone}")

                try:
                    send_verification_sms(user.phone, code)
                    messages.info(request, 'کد تأیید به شماره شما ارسال شد.')
                    return redirect('verify-phone')
                except Exception as e:
                    logger.error(f"📲 SMS sending failed to {user.phone} - {e}")
                    messages.error(request, f'خطا در ارسال پیامک: {e}')
                    return redirect('login')
        else:
            logger.warning("⚠️ Invalid login form submitted.")
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


logger = logging.getLogger('user')
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

            email_msg = EmailMultiAlternatives(
                subject='لینک ورود',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            logger.info(f"📧 Login link sent to user: {user.username} (email: {user.email})")
            return render(request, 'user/email_sent.html')
        except User.DoesNotExist:
            logger.warning(f"❌ Login link request failed - No user found with email: {email}")
            return render(request, 'user/send_link.html', {'error': 'ایمیل پیدا نشد.'})
    return render(request, 'user/send_link.html')

logger = logging.getLogger('user')
def confirm_login_link_view(request, token):
    email = verify_token(token)
    if not email:
        logger.warning("❌ Login link verification failed - Invalid or expired token.")
        messages.error(request, 'لینک ورود منقضی شده یا نامعتبر است.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login(request, user)

        logger.info(f"✅ User logged in via link: {user.username} (email: {email})")
        return redirect('home')
    except CustomUser.DoesNotExist:
        logger.error(f"❌ Login link failed - User not found with email: {email}")
        messages.error(request, 'کاربر یافت نشد.')
        return redirect('login')

logger = logging.getLogger('user')
def password_reset_view(request, token):
    email = verify_token(token)
    if not email:
        logger.warning("❌ Password reset failed - Invalid or expired token.")
        return render(request, 'user/invalid_token.html')

    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"🔐 Password reset token verified for user: {user.username} (email: {email})")
    except CustomUser.DoesNotExist:
        logger.error(f"❌ Password reset failed - No user found with email: {email}")
        return render(request, 'user/invalid_token.html')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            logger.info(f"✅ Password changed successfully for user: {user.username} (email: {email})")
            messages.success(request, "رمز عبور با موفقیت تغییر کرد.")
            return redirect('login')
        else:
            logger.warning(f"⚠️ Invalid password reset form submitted for user: {user.username}")
    else:
        form = PasswordChangeForm()

    return render(request, 'user/password_reset.html', {'form': form})

import logging
logger = logging.getLogger('user')

logger = logging.getLogger('user')
def signin_view(request):
    if request.method == 'POST':
        form = signinForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data['password']
            second_password = form.cleaned_data['second_password']

            # بررسی ایمیل تکراری
            if email and CustomUser.objects.filter(email=email).exists():
                messages.error(request, "کاربری با این ایمیل قبلاً ثبت‌نام کرده است.")
                logger.warning(f"❌ Duplicate email attempted during signup: {email}")
                return render(request, 'user/sign_in.html', {'form': form})

            logger.info(f"🆕 New user registration initiated: {username}")

            # ساخت کاربر
            user = CustomUser(username=username, email=email, phone=phone)
            user.set_password(password)
            user.save()
            logger.info(f"✅ User account created: {user.username}")

            # هش و ذخیره رمز دوم
            hashed_second_password = custom_simple_hash(second_password)
            UserSecondPassword.objects.create(
                user=user,
                hashed_password=hashed_second_password
            )
            logger.info(f"🔐 Second password stored for user: {user.username}")

            # ارسال پیامک یا ایمیل خوش‌آمدگویی
            if phone:
                logger.info(f"📲 Sending welcome SMS to: {phone}")
                send_verification_sms(phone, "ثبت‌نام شما با موفقیت انجام شد.")
            elif email:
                logger.info(f"📧 Sending welcome email to: {email}")
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
            logger.warning("❗ Invalid signup form submitted.")

    else:
        form = signinForm()

    return render(request, 'user/sign_in.html', {'form': form})



logger = logging.getLogger('user')
def user_profile_view(request, slug):
    user = get_object_or_404(User, slug=slug)
    logger.info(f"👤 Profile viewed: {user.username} (ID: {user.id}) by {request.user if request.user.is_authenticated else 'Anonymous'}")
    return render(request, 'user/profile.html', {'profile_user': user})

logger = logging.getLogger('user')
def profile_view(request, slug):
    user = get_object_or_404(User, slug=slug)
    logger.info(f"👤 Profile viewed: {user.username} (ID: {user.id}) by {request.user if request.user.is_authenticated else 'Anonymous'}")
    return render(request, 'user/profile.html', {'profile_user': user})


logger = logging.getLogger('user')
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

                    logger.info(f"📧 Password reset link sent to email: {user.email}")
                    messages.success(request, "لینک تغییر رمز به ایمیل شما ارسال شد.")
                    return redirect('login')

                else:
                    user = CustomUser.objects.get(phone=contact)
                    code = str(random.randint(100000, 999999))
                    request.session['reset_code'] = code
                    request.session['reset_phone'] = user.phone

                    send_verification_sms(user.phone, code)
                    logger.info(f"📲 Password reset code sent to phone: {user.phone}")
                    return redirect('verify_reset_code')

            except CustomUser.DoesNotExist:
                logger.warning(f"❌ Password reset attempt failed - no user found with contact: {contact}")
                messages.error(request, "کاربری با این اطلاعات پیدا نشد.")
    else:
        form = passwordResetForm()

    return render(request, 'user/passwordreset_email.html', {'form': form})


logger = logging.getLogger('user')
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
                    logger.info(f"📧 Password reset link generated and verified for: {contact}")
                    messages.success(request, 'لینک تغییر رمز به ایمیل شما ارسال شد.')
                else:
                    user = CustomUser.objects.get(phone=contact)
                    send_verification_sms(user.phone, purpose='reset_password')
                    request.session['reset_phone'] = user.phone
                    logger.info(f"📲 Password reset SMS sent to: {contact}")
                    return redirect('verify_reset_code')
            except CustomUser.DoesNotExist:
                logger.warning(f"❌ Password reset failed - user not found with contact: {contact}")
                messages.error(request, 'کاربری با این اطلاعات یافت نشد.')
    else:
        form = passwordResetForm()

    return render(request, 'user/forgot_password.html', {'form': form})

logger = logging.getLogger('user')


logger = logging.getLogger('user')
def password_reset_link_view(request, token):
    email = verify_token(token)
    if not email:
        logger.warning("❌ Invalid or expired password reset token.")
        messages.error(request, 'لینک بازنشانی رمز منقضی یا نامعتبر است.')
        return redirect('login')

    try:
        user = CustomUser.objects.get(email=email)
        logger.info(f"🔓 Password reset link verified for: {email}")
    except CustomUser.DoesNotExist:
        logger.error(f"❌ User not found with email during password reset: {email}")
        messages.error(request, "کاربری با این ایمیل یافت نشد.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()

            logger.info(f"✅ Password successfully reset for user: {email}")
            messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت.')
            return redirect('login')
        else:
            logger.warning(f"❌ Invalid password reset form submitted for {email}")
    else:
        form = PasswordChangeForm()

    return render(request, 'user/password_reset.html', {'form': form})

logger = logging.getLogger('user')
def verify_phone_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        otp_code = request.session.get('otp_code')
        user_id = request.session.get('otp_user_id')

        if not (code and otp_code and user_id):
            logger.warning("❌ Incomplete OTP verification data in session.")
            messages.error(request, 'اطلاعات ناقص است. لطفاً دوباره تلاش کنید.')
            return redirect('login')

        if code == otp_code:
            try:
                user = User.objects.get(id=user_id)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                logger.info(f"✅ User logged in via phone: {user.phone}")

                # پاک‌سازی session پس از ورود موفق
                request.session.pop('otp_code', None)
                request.session.pop('otp_user_id', None)

                messages.success(request, f"{user.username} عزیز، خوش آمدی!")
                return redirect('home')

            except User.DoesNotExist:
                logger.error(f"❌ User not found with ID during OTP login: {user_id}")
                messages.error(request, 'کاربر یافت نشد.')
        else:
            logger.warning("❌ Incorrect OTP entered during login.")
            messages.error(request, 'کد وارد شده اشتباه است.')

    return render(request, 'user/verify_phone.html')


logger = logging.getLogger('user')
def verify_reset_code_view(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        session_code = request.session.get('reset_code')
        phone = request.session.get('reset_phone')

        if not all([entered_code, session_code, phone]):
            logger.warning("❌ اطلاعات ناقص در جلسه برای تأیید کد بازنشانی.")
            messages.error(request, 'اطلاعات ناقص است. لطفاً دوباره تلاش کنید.')
            return redirect('password-reset')

        if entered_code == session_code:
            try:
                user = User.objects.get(phone=phone)
                request.session['password_reset_user_id'] = user.id
                # پاک‌سازی session
                request.session.pop('reset_code', None)
                request.session.pop('reset_phone', None)

                logger.info(f"✅ کد بازنشانی صحیح وارد شد برای شماره: {phone}")
                return redirect('password-reset-confirm')
            except User.DoesNotExist:
                logger.error(f"❌ کاربری با شماره {phone} یافت نشد.")
                messages.error(request, 'کاربر یافت نشد.')
        else:
            logger.warning("❌ کد اشتباه برای بازنشانی وارد شد.")
            messages.error(request, 'کد وارد شده صحیح نیست.')

    return render(request, 'user/verify_reset_code.html')


def password_reset_confirm_view(request):
    user_id = request.session.get('password_reset_user_id')

    if not user_id:
        logger.warning("❌ تلاش برای دسترسی غیرمجاز یا منقضی‌شده به بازنشانی رمز عبور.")
        messages.error(request, "دسترسی نامعتبر یا جلسه منقضی شده است.")
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        logger.error(f"❌ کاربری با ID {user_id} برای تأیید بازنشانی یافت نشد.")
        messages.error(request, "کاربر یافت نشد.")
        return redirect('login')

    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['new_password']
            user.set_password(password)
            user.save()

            request.session.pop('password_reset_user_id', None)

            logger.info(f"🔐 رمز عبور با موفقیت تغییر یافت برای کاربر: {user.username}")
            messages.success(request, "رمز عبور شما با موفقیت تغییر یافت.")
            return redirect('login')
        else:
            logger.warning("❌ فرم تغییر رمز عبور معتبر نیست.")
            messages.error(request, "لطفاً فرم را به‌درستی تکمیل کنید.")
    else:
        form = PasswordChangeForm()

    return render(request, 'user/password_reset.html', {'form': form})
