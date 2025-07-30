print("===== CUSTOM COMMAND LOADED =====")

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'ساخت ۱۰ کاربر تستی برای بررسی'

    def handle(self, *args, **kwargs):
        for i in range(1, 11):
            username = f'testuser{i}'
            email = f'testuser{i}@example.com'
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, email=email, password='test1234')
                self.stdout.write(self.style.SUCCESS(f'کاربر {username} با موفقیت ایجاد شد.'))
            else:
                self.stdout.write(self.style.WARNING(f'کاربر {username} قبلاً وجود داشته.'))
