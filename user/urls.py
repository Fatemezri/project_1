from django.urls import path
from .views import login_view, confirm_login_link_view, send_login_link_view,signin_view, home


urlpatterns = [
    path('login/', login_view, name = 'login'),
    path('home/', home, name ='home'),
    path('login/email/', send_login_link_view, name='send-login-link'),
    path('login/email/confirm/<str:token>/', password_reset_link_view, name='confirm-login-link'),
    path('signin/', signin_view, name='signin'),
    path('password-reset/', PasswordReset_email_view, name='PasswordReset_email'),
    path('users/<slug:slug>/',user_profile_view, name='profile'),
    path('reset/<str:token>/', password_reset_link_view, name='password-reset'),
    path('login-confirm/<str:token>/', confirm_login_link_view, name='confirm-login-link'),
    path('verify-phone/', verify_phone_view, name='verify-phone'),

]

