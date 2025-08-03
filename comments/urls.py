# comments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.comment_list, name='comment_list'),
    path('submit/', views.submit_comment, name='submit_comment'),
]