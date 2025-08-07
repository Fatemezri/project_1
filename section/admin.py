from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Section
from .forms import SectionAdminForm
import logging
logger = logging.getLogger('section')


@admin.register(Section)
class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = SectionAdminForm
    list_display = ['title', 'parent', 'tree_order']
    list_filter = ['parent']

    def tree_order(self, obj):
        parts = []
        current = obj
        while current:
            siblings = list(Section.objects.filter(parent=current.parent).order_by('order'))
            index = siblings.index(current) + 1
            parts.insert(0, str(index))
            current = current.parent
        order_str = ".".join(parts)
        logger.debug(f"Computed tree_order for section '{obj.title}': {order_str}")
        return order_str

    tree_order.short_description = "ترتیب"