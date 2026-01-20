"""
Custom Authentication Backend for ZoeFit

This authentication backend allows users to authenticate using their email address
instead of username, which is more user-friendly for modern applications.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class EmailBackend(BaseBackend):
    """
    Custom authentication backend that authenticates users using their email address.
    """
    
    def authenticate(self, request, email=None, password=None, username=None, **kwargs):
        """
        Authenticate user using email and password.
        """
        # Support both email and username authentication
        identifier = email or username
        
        if not identifier:
            return None
            
        try:
            # Try to find user by email first, then by username
            user = User.objects.get(email=identifier)
        except ObjectDoesNotExist:
            try:
                user = User.objects.get(username=identifier)
            except ObjectDoesNotExist:
                return None
        
        if user.check_password(password):
            return user
        return None
    
    def get_user(self, user_id):
        """
        Retrieve user by user ID.
        """
        try:
            user = User.objects.get(pk=user_id)
            return user
        except ObjectDoesNotExist:
            return None
