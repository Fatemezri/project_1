from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.superuser_messages, name='superuser_messages'),
]