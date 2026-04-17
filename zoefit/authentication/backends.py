"""
Custom email-based authentication for ZoeFit

Django's default authentication uses usernames, but most people
remember their email address better than a random username they chose
years ago. This custom backend lets users log in with either.

How it works:
1. Try to find user by email first
2. If no email match, try username (for backward compatibility)
3. Verify the password matches the stored hash
4. Return the user object if everything checks out

This approach gives users flexibility while maintaining security.
We still store usernames in the database for display purposes,
but authentication is primarily email-based.
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class EmailBackend(BaseBackend):
    """
    Email-first authentication backend for ZoeFit users.
    
    Instead of forcing users to remember their username,
    we let them log in with the email they use every day.
    Much more user-friendly!
    
    We still support username login for backward compatibility
    and for users who prefer it.
    """
    
    def authenticate(self, request, email=None, password=None, username=None, **kwargs):
        """
        Try to authenticate a user with email/username and password.
        
        We prioritize email since that's what most users remember,
        but fall back to username for compatibility.
        
        Returns the User object if credentials are valid,
        or None if authentication fails.
        """
        # Use whichever identifier the user provided
        identifier = email or username
        
        if not identifier or not password:
            return None
            
        try:
            # First try looking up by email (most common case)
            user = User.objects.get(email=identifier)
        except ObjectDoesNotExist:
            try:
                # Fall back to username lookup
                user = User.objects.get(username=identifier)
            except ObjectDoesNotExist:
                # No user found with either email or username
                return None
        
        # Check if the password is correct
        if user.check_password(password):
            return user
        
        # Password doesn't match
        return None
    
    def get_user(self, user_id):
        """
        Retrieve a user by their primary key ID.
        
        Django calls this method on each request to reload the user
        from the database. This ensures we always have the most
        up-to-date user data.
        
        Returns None if the user doesn't exist (account deleted).
        """
        try:
            user = User.objects.get(pk=user_id)
            return user
        except ObjectDoesNotExist:
            # User was deleted or ID is invalid
            return None
