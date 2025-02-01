# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import BaseBackend

# User = get_user_model()

# class EmailAuthBackend(BaseBackend):
#     def authenticate(self, request, email=None, password=None):
#         try:
#             user = User.objects.get(email=email)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            logger.info(f"Found user: {user}")
            if user.check_password(password):
                return user
            else:
                logger.warning(f"Incorrect password for user: {email}")
        except User.DoesNotExist:
            logger.error(f"User with email {email} does not exist")
        return None
