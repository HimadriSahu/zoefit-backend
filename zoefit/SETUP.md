# ZoeFit Backend Setup Guide

## Authentication Module Setup

The authentication module has been set up with JWT authentication. Follow these steps to get started:

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Virtual environment (recommended)

## Installation Steps

1. **Activate virtual environment** (if using one):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**:
   - Ensure PostgreSQL is running
   - Create database `zoefit_db` (or update settings.py with your database name)
   - Update database credentials in `zoefit/settings.py` if needed

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication Endpoints

- **POST** `/api/auth/register/` - User registration
- **POST** `/api/auth/login/` - User login
- **POST** `/api/auth/logout/` - User logout (requires authentication)
- **POST** `/api/auth/token/refresh/` - Refresh access token
- **GET** `/api/auth/profile/` - Get user profile (requires authentication)
- **PUT/PATCH** `/api/auth/profile/update/` - Update user profile (requires authentication)

### Example Registration Request

```json
POST /api/auth/register/
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "height": 175.0,
  "weight": 70.0,
  "fitness_goal": "weight_loss"
}
```

### Example Login Request

```json
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Using Authenticated Endpoints

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Project Structure

```
zoefit/
├── authentication/          # Authentication module
│   ├── models.py           # User model
│   ├── serializers.py      # API serializers
│   ├── views.py            # API views
│   ├── urls.py             # URL routing
│   └── admin.py            # Admin configuration
├── api/                     # Other API modules (for future use)
├── zoefit/                  # Project settings
│   ├── settings.py         # Django settings
│   └── urls.py             # Main URL configuration
└── requirements.txt        # Python dependencies
```

## Notes

- The `api` app has been commented out and is reserved for future modules
- All authentication endpoints are under `/api/auth/`
- JWT tokens expire after 60 minutes (access) and 7 days (refresh)
- Media files (profile pictures) are stored in `media/profile_pictures/`

## Next Steps

1. Test the authentication endpoints using Postman or similar tool
2. Integrate with your Expo Go frontend
3. Add additional modules as needed (workouts, nutrition, etc.)

