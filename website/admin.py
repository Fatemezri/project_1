from django.contrib import admin
from comment_app.models import Comment
from report_app.models import Message
from django.contrib import messages
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


# ایجاد یک کلاس AdminSite سفارشی برای پنل مدیریت مدیران
class ModeratorAdminSite(admin.AdminSite):
    site_header = "پنل مدیریت مدیران"
    site_title = "پنل مدیریت مدیران"
    index_title = "داشبورد مدیریت"
    login_template = 'moderator_admin/login.html'
    index_template = 'moderator_admin/index.html'

    def has_permission(self, request: HttpRequest) -> bool:
        """
        این متد بررسی می‌کند که آیا کاربر ناظر و دارای مجوزهای لازم است.
        فقط کاربرانی که is_staff هستند، سوپریوزر نیستند و مجوزهای مشخصی دارند، اجازه دسترسی دارند.
        """
        user = request.user

        # بررسی اینکه آیا کاربر فعال و از نوع staff است.
        if not (user.is_active and user.is_staff):
            return False

        # بررسی اینکه آیا کاربر سوپریوزر است. اگر باشد، اجازه دسترسی ندارد.
        if user.is_superuser:
            return False

        # بررسی مجوزهای مشخص برای کامنت‌ها
        return (
                user.has_perm('comment_app.add_comment') or
                user.has_perm('comment_app.change_comment') or
                user.has_perm('comment_app.view_comment')
        )


# ایجاد نمونه‌ای از سایت ادمین سفارشی برای مدیران
moderator_admin_site = ModeratorAdminSite(name='moderator_admin')


# کلاس Admin سفارشی برای کامنت‌ها در پنل مدیران
@admin.register(Comment, site=moderator_admin_site)
class CommentModeratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "کامنت‌های انتخاب شده تایید شدند.", level=messages.SUCCESS)

    approve_comments.short_description = "تایید کامنت‌های انتخاب شده"

    # فقط کامنت‌های تایید نشده را نمایش می‌دهد
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
        # اجازه مشاهده فقط برای پیام‌هایی که خودشان ارسال کرده‌اند
        return obj is None or obj.sender == request.user

    # فقط فیلد محتوا را در فرم اضافه کردن پیام نمایش می‌دهد
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['fields'] = ['content']
        return super().get_form(request, obj, **kwargs)

    # به صورت خودکار فرستنده را به کاربر فعلی و گیرنده را به یک سوپریوزر خاص تنظیم می‌کند
    def save_model(self, request, obj, form, change):
        if not change:
            obj.sender = request.user
            try:
                # بسیار مهم: اطمینان حاصل کنید که یک سوپریوزر با نام کاربری 'fateme' ایجاد کرده‌اید.
                # در غیر این صورت، پیام‌ها به هیچ کاربری ارسال نمی‌شوند.
                superuser = User.objects.get(username='fateme')
                # گیرنده را به سوپریوزر پیدا شده تنظیم می‌کند
                obj.recipient = superuser
                # کامنت اصلی را با مقادیر پر شده ذخیره می‌کند
                super().save_model(request, obj, form, change)
            except User.DoesNotExist:
                # اگر سوپریوزر پیدا نشد، یک پیام هشدار نمایش می‌دهد و پیام را ذخیره نمی‌کند
                self.message_user(request, "کاربر 'fateme' به عنوان سوپریوزر وجود ندارد. پیام ارسال نشد.",
                                  level=messages.WARNING)
        else:
            # برای ویرایش، رفتار پیش‌فرض را اجرا می‌کند
            super().save_model(request, obj, form, change)

