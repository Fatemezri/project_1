from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_comment, name='submit_comment'),
    path('success/', views.comment_success, name='comment_success'),
]