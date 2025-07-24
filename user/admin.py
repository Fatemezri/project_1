from django.contrib import admin
class MassEmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_at']
    actions = ['send_email_to_all']

    def send_email_to_all(self, request, queryset):

        subject = mass_email.subject
        html_message = mass_email.html_message
        from_email = settings.DEFAULT_FROM_EMAIL

        # همه کاربرانی که ایمیل دارند
        recipients = CustomUser.objects.exclude(email='').values_list('email', flat=True)

        if not recipients:
            self.message_user(request, "هیچ کاربری با ایمیل معتبر یافت نشد.", level=messages.WARNING)
            return

        # ساخت و ارسال ایمیل
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=from_email,
            to=[],
            bcc=recipients,  # ایمیل به صورت BCC ارسال شود تا لیست دیده نشود
        )
        email.content_subtype = "html"

        try:
            email.send()
            self.message_user(request, f"{len(recipients)} ایمیل با موفقیت ارسال شد.", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"خطا در ارسال ایمیل: {str(e)}", level=messages.ERROR)

    send_email_to_all.short_description = "ارسال ایمیل به همه کاربران"

admin.site.register(MassEmail, MassEmailAdmin)


from django.utils.html import format_html

# Register your models here.
