
from django.urls import path, include
from django.contrib import admin
from .admin import moderator_admin_site


urlpatterns = [
    path('admin/', admin.site.urls),
    # این پنل ادمین سفارشی است که فقط برای مدیران ناظر طراحی شده است.
    path('moderator-admin/', moderator_admin_site.urls),
    path('comments/', include('comment_app.urls')),
    path('report/', include('report_app.urls')),
    path('', include('user.urls')),
    path('accounts/', include('allauth.urls')),

]