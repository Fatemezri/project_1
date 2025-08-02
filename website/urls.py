from django.contrib import admin
from django.urls import path, include
from comments.admin_site import moderator_admin_site


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('accounts/', include('allauth.urls')),
    path('moderator-admin/', moderator_admin_site.urls),
    path('comments/', include('comments.urls')),

]



