from django.apps import AppConfig

class CommentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comments'
    verbose_name = "نظرات و اعلانات"

    def ready(self):
        # Import the signals module to register the handlers
        import comments.signals
