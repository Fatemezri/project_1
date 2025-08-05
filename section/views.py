from django.shortcuts import render
from .models import Section

def section_list(request):
    sections = Section.objects.filter(parent=None).order_by('order')
    return render(request, 'sections_list.html', {'sections': sections})