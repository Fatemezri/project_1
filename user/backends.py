#چون نمیخواهیم با username  لاگین کنیم یک custom authentication backend تعریف میکنیم

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class UsernameAndContactBackend(BaseBackend):
    def authenticate(self, request, username=None, contact=None, password=None, **kwargs):
        try:
            if contact and '@' in contact:
                user = UserModel.objects.get(username=username, email=contact)
            else:
                user = UserModel.objects.get(username=username, phone=contact)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
