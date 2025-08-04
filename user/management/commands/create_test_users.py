# D:\PROJECT\MIZAN_GOSTAR\PROJECT\USER\management\commands\create_test_users.py

import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# دریافت مدل کاربر
User = get_user_model()

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'ساخت ۱۰ کاربر تستی برای بررسی'

    def handle(self, *args, **kwargs):
        logger.info("===== CUSTOM COMMAND LOADED =====")
        self.stdout.write(self.style.SUCCESS('===== CUSTOM COMMAND LOADED ====='))
        logger.info('Starting command to create test users.')

        for i in range(1, 11):
            username = f'testuser{i}'
            email = f'testuser{i}@example.com'

            try:
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(username=username, email=email, password='test1234')
                    self.stdout.write(self.style.SUCCESS(f'کاربر {username} با موفقیت ایجاد شد.'))
                    logger.info(f'✅ User {username} created successfully.')
                else:
                    self.stdout.write(self.style.WARNING(f'کاربر {username} قبلاً وجود داشته.'))
                    logger.warning(f'⚠️ User {username} already exists. Skipping creation.')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'خطا در ایجاد کاربر {username}: {e}'))
                logger.error(f'❌ Error creating user {username}: {e}', exc_info=True)

        logger.info('Finished creating test users command.')