from django.shortcuts import render
from .models import Section
import logging
logger = logging.getLogger('section_app')

def section_list(request):
    logger.info(f"Section list requested by user: {request.user.username}")
    sections = Section.objects.filter(parent=None).order_by('order')
    logger.debug(f"Found {sections.count()} root sections.")
    return render(request, 'sections_list.html', {'sections': sections})