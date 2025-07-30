from django.contrib import admin
from django.urls import path, include
from . import views
from comments.views import submit_comment, admin_panel, approve_comment



urlpatterns = [
    path('admin/', admin.site.urls),
    path("manager/", views.manager_dashboard),
    path("comments/", include("comments.urls")),
    path('', include('user.urls')),
    path('accounts/', include('allauth.urls')),


]



