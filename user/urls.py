from tkinter.font import names

from django.urls import path
from .views import login_view, password_reset_link_view, send_login_link_view,signin_view, \
    PasswordReset_email_view,user_profile_view,\
    PasswordReset_email_view,password_reset_link_view,confirm_login_link_view,verify_phone_view,\
    home,verify_reset_code_view,password_reset_confirm_view,index


urlpatterns = [
    path('', index, name='index'),
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
    path('password/verify-code/', verify_reset_code_view, name='password-verify-code'),
    path('password/verify_reset_code', verify_reset_code_view, name= 'verify_reset_code'),
    path('password/reset/confirm/', password_reset_confirm_view, name='password-reset-confirm')

]

