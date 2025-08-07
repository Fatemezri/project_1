from django.contrib import admin
from comment_app.models import Comment
from report_app.models import Message
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
import logging
logger = logging.getLogger('moderator_admin')



class ModeratorAdminSite(admin.AdminSite):
    site_header = "پنل مدیریت مدیران"
    site_title = "پنل مدیریت مدیران"
    index_title = "داشبورد مدیریت"
    login_template = 'moderator_admin/login.html'
    index_template = 'moderator_admin/index.html'

    def has_permission(self, request: HttpRequest) -> bool:

        user = request.user


        if not (user.is_active and user.is_staff):
            logger.warning(f"Access denied for inactive or non-staff user: {user}")
            return False


        if user.is_superuser:
            logger.warning(f"Access denied for superuser: {user}")
            return False

        logger.info(f"Access granted to moderator: {user}")
        return (
                user.has_perm('comment_app.add_comment') or
                user.has_perm('comment_app.change_comment') or
                user.has_perm('comment_app.view_comment')
        )



moderator_admin_site = ModeratorAdminSite(name='moderator_admin')



@admin.register(Comment, site=moderator_admin_site)
class CommentModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        count=queryset.update(is_approved=True)
        logger.info(f"{count} comments approved by moderator: {request.user}")
        self.message_user(request, "کامنت‌های انتخاب شده تایید شدند.", level=messages.SUCCESS)

    approve_comments.short_description = "تایید کامنت‌های انتخاب شده"


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_approved=False)

    # مدیران پیام فقط می‌توانند کامنت‌ها را تایید کنند و نمی‌توانند اضافه، حذف یا ویرایش کنند
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True


# کلاس Admin سفارشی برای پیام‌ها در پنل مدیران
@admin.register(Message, site=moderator_admin_site)
class MessageModeratorAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'content', 'created_at')

    # متدهای مربوط به مجوزها
    def has_add_permission(self, request):
        return True  # اجازه اضافه کردن پیام

    def has_change_permission(self, request, obj=None):
        return False  # عدم اجازه ویرایش

    def has_delete_permission(self, request, obj=None):
        return False  # عدم اجازه حذف

    def has_view_permission(self, request, obj=None):
        return obj is None or obj.sender == request.user

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['fields'] = ['content']
        return super().get_form(request, obj, **kwargs)


    def save_model(self, request, obj, form, change):
        if not change:
            obj.sender = request.user
            try:

                superuser = User.objects.get(username='fateme')
                obj.recipient = superuser
                logger.info(f"New message created by {request.user} for superuser {superuser}")
                super().save_model(request, obj, form, change)
            except User.DoesNotExist:
                logger.error("Superuser 'fateme' does not exist. Message not saved.")
                self.message_user(request, "کاربر 'fateme' به عنوان سوپریوزر وجود ندارد. پیام ارسال نشد.",
                                  level=messages.WARNING)
        else:
            logger.info(f"Message edited by {request.user}")
            super().save_model(request, obj, form, change)

