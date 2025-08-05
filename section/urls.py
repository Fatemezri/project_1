from django.urls import path
from .views import section_list

urlpatterns = [
    path('', section_list, name='section_list'),
]