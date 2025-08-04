# your_app/forms.py
from django import forms
from .models import Section

class SectionAdminForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()


        if not self.instance.pk and Section.objects.count() >= 7:
            raise forms.ValidationError("حداکثر ۷ سکشن قابل افزودن است.")


        parent = cleaned_data.get('parent')
        current_level = 0
        if parent:
            current_level = parent.get_level() + 1 # سطح فعلی = سطح والد + 1

        if current_level > 2:
            raise forms.ValidationError("عمق بیش از ۳ سطح مجاز نیست. (سطح 0، 1 و 2)")

        return cleaned_data