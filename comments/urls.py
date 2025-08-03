from django.urls import path
from . import views
from .admin_site import moderator_admin_site

app_name = 'comments'
urlpatterns = [
    path('submit-comment/', views.submit_comment, name='submit_comment'),
    path('moderator-admin/', moderator_admin_site.urls),
]
