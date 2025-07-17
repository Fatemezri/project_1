from django.urls import path
from .views import login_view, confirm_login_link_view, send_login_link_view, home


urlpatterns = [
    path('login/', login_view, name = 'login'),
    path('home/', home, name = 'home'),
    path('login/email/', send_login_link_view, name='send-login-link'),
    path('login/email/confirm/<str:token>/', confirm_login_link_view, name='confirm-login-link'),
]

