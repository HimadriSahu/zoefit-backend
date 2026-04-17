# Authentication Module

This module handles user authentication, registration, and profile management for the ZoeFit application.

## Features

- JWT-based authentication
- User registration with email and password
- User login
- User profile management
- Token refresh
- Token blacklisting (logout)

## API Endpoints

### Registration
- **POST** `/api/auth/register/`
  - Body: `{ "email": "user@example.com", "username": "username", "password": "password123", "password2": "password123", ... }`
  - Returns: User data and JWT tokens

### Login
- **POST** `/api/auth/login/`
  - Body: `{ "email": "user@example.com", "password": "password123" }`
  - Returns: User data and JWT tokens

### Logout
- **POST** `/api/auth/logout/`
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ "refresh_token": "your_refresh_token" }`
  - Returns: Success message

### Token Refresh
- **POST** `/api/auth/token/refresh/`
  - Body: `{ "refresh": "your_refresh_token" }`
  - Returns: New access token

### Get Profile
- **GET** `/api/auth/profile/`
  - Headers: `Authorization: Bearer <access_token>`
  - Returns: User profile data

### Update Profile
- **PUT/PATCH** `/api/auth/profile/update/`
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ "first_name": "John", "last_name": "Doe", ... }`
  - Returns: Updated user profile

### Change Password
- **POST** `/api/auth/change-password/`
  - Headers: `Authorization: Bearer <access_token>`
  - Body: `{ "old_password": "current_password", "new_password": "new_password", "new_password2": "new_password" }`
  - Returns: Success message

## User Model

The custom User model extends Django's AbstractUser and includes:
- Email (used as username)
- Phone number
- Date of birth
- Profile picture
- Height and weight
- Fitness goal

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Usage

All endpoints except registration and login require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

