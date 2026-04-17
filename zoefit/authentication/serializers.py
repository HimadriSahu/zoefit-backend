"""
API serializers for user authentication

This module contains all serializers for the authentication API.
Serializers handle:
- User registration with validation
- User login with authentication
- User profile data serialization

These serializers convert user data between Python objects and JSON.
They also handle validation - making sure passwords match, emails are valid, etc.

Think of serializers as translators: they take complex Python objects
and turn them into simple JSON that the frontend can understand.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Handles new user sign-ups.
    
    We collect the minimum info needed to create an account:
    - username: for display purposes (optional, can be auto-generated)
    - email: for login and communications (required)
    - password: for security (required)
    - password2: to catch typos (required)
    
    The serializer automatically hashes passwords, so we never store
    plain text passwords in the database.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'password2',
        )
    
    def validate(self, attrs):
        """
        Make sure both password fields match.
        
        It's easy to make a typo when entering a password, so we ask
        twice and compare. This prevents users from locking themselves out.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        """
        Create the new user account.
        
        We use Django's create_user() method which automatically:
        - Hashes the password using bcrypt
        - Sets up the user properly in the database
        - Handles all the security stuff we don't want to mess with
        """
        validated_data.pop('password2')
        password = validated_data.pop('password')
        # create_user handles password hashing automatically
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Handles user login requests.
    
    Simple and straightforward - just need email and password.
    If they match, we return the user object for the view to create tokens.
    
    We don't store any session data here - that's handled by JWT tokens
    in the view layer.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Check if the email and password combination is valid.
        
        Uses Django's built-in authenticate() function which:
        - Checks the password against the stored hash
        - Verifies the user account is active
        - Returns None if anything doesn't match
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Try to authenticate using email
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            
            if not user:
                # Either the email doesn't exist or password is wrong
                # We don't specify which to prevent email enumeration attacks
                raise serializers.ValidationError(
                    'Invalid email or password. Please try again.'
                )
            
            if not user.is_active:
                # User account has been deactivated
                raise serializers.ValidationError(
                    'This account has been disabled. Contact support if this is a mistake.'
                )
            
            attrs['user'] = user
            return attrs
        else:
            # Missing required fields
            raise serializers.ValidationError(
                'Please provide both email and password to login.'
            )

