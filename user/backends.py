#چون نمیخواهیم با username  لاگین کنیم یک custom authentication backend تعریف میکنیم

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

# دریافت مدل کاربر
UserModel = get_user_model()

# دریافت لاگر برای این فایل
logger = logging.getLogger(__name__)


class UsernameAndContactBackend(BaseBackend):
    def authenticate(self, request, username=None, contact=None, password=None, **kwargs):
        """
        احراز هویت کاربر با استفاده از نام کاربری و ایمیل یا شماره همراه.
        """
        logger.info(f"Attempting to authenticate user '{username}' with contact '{contact}'.")
        try:
            if contact and '@' in contact:
                logger.debug(f"Authenticating by email: '{contact}'.")
                user = UserModel.objects.get(username=username, email=contact)
            else:
                logger.debug(f"Authenticating by phone: '{contact}'.")
                user = UserModel.objects.get(username=username, phone=contact)

            logger.debug(f"User '{username}' found. Checking password.")
            if user.check_password(password):
                logger.info(f"✅ User '{username}' authenticated successfully.")
                return user
            else:
                logger.warning(f"❌ Authentication failed for user '{username}': password mismatch.")
                return None
        except UserModel.DoesNotExist:
            logger.warning(
                f"❌ Authentication failed for user '{username}': user with contact '{contact}' does not exist.")
            return None
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred during authentication: {e}", exc_info=True)
            return None

    def get_user(self, user_id):
        """
        بازیابی شیء کاربر بر اساس user_id.
        """
        logger.info(f"Attempting to retrieve user with ID: {user_id}")
        try:
            user = UserModel.objects.get(pk=user_id)
            logger.debug(f"✅ User with ID {user_id} found.")
            return user
        except UserModel.DoesNotExist:
            logger.warning(f"❌ User with ID {user_id} does not exist.")
            return None
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred while retrieving user with ID {user_id}: {e}", exc_info=True)
            return None