from django.apps import AppConfig

class CommentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comment_app'

    def ready(self):
        # سیگنال‌ها را وارد می‌کند تا مطمئن شود بارگذاری شده‌اند
        import comment_app.signals