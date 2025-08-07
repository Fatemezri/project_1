#چون نمیخواهیم با username  لاگین کنیم یک custom authentication backend تعریف میکنیم

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
UserModel = get_user_model()
import logging
logger = logging.getLogger('user')

class UsernameAndContactBackend(BaseBackend):
    def authenticate(self, request, username=None, contact=None, password=None, **kwargs):
        try:
            if contact and '@' in contact:
                user = UserModel.objects.get(username=username, email=contact)
            else:
                user = UserModel.objects.get(username=username, phone=contact)
            if user.check_password(password):
                logger.info(f"User authenticated successfully: {username} - {contact}")
                return user
            else:
                logger.warning(f"Invalid password for user: {username} - {contact}")
                return None
        except UserModel.DoesNotExist:
            logger.warning(f"Authentication failed: user not found for username={username}, contact={contact}")
            return None

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
            logger.debug(f"User retrieved successfully by ID: {user_id}")
            return user
        except UserModel.DoesNotExist:
            logger.warning(f"User not found for ID: {user_id}")
            return None
