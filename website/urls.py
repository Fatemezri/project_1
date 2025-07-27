from django.contrib import admin
from django.urls import path, include
from user import views as user_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),  # مسیرهای اپ user
    path('accounts/', include('allauth.urls')),  # مسیر ورود با گوگل
]



