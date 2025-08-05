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
        if self.instance.get_level() > 2:
            raise forms.ValidationError("عمق بیش از ۳ سطح مجاز نیست.")
        return cleaned_data