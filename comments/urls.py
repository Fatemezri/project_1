from django.urls import path
from . import views

app_name = 'comments'
urlpatterns = [
    path('submit-comment/', views.submit_comment, name='submit_comment'),
]