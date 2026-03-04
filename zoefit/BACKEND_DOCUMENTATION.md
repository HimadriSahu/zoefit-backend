# ZoeFit Backend Documentation

## Overview

ZoeFit is a Django-based REST API for a fitness application with clean separation between authentication and user profile management.

## Architecture

### Module Structure

```
zoefit/
├── authentication/     # User authentication & authorization
├── profiles/          # User profile & fitness data
├── zoefit/           # Project configuration
└── manage.py         # Django management script
```

### Design Principles

- **Separation of Concerns**: Authentication logic separated from profile data
- **JWT Authentication**: Token-based authentication with refresh tokens
- **Clean API Design**: RESTful endpoints with clear responsibilities
- **Minimal Dependencies**: Only essential packages included

## API Endpoints

### Authentication Module (`/api/auth/`)

#### User Registration
```
POST /api/auth/register/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password2": "securepassword123"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "john@example.com",
        "username": "johndoe"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### User Login
```
POST /api/auth/login/
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

#### Token Refresh
```
POST /api/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### User Logout
```
POST /api/auth/logout/
Content-Type: application/json
Authorization: Bearer <access_token>

{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Password Management
```
POST /api/auth/forgot-password/
POST /api/auth/change-password/
```

### Profiles Module (`/api/profiles/`)

#### Create Profile
```
POST /api/profiles/profile/create/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "height": 175.5,
    "weight": 70.0,
    "fitness_goal": "muscle_gain",
    "bio": "Fitness enthusiast",
    "location": "New York"
}
```

#### Get Profile
```
GET /api/profiles/profile/
Authorization: Bearer <access_token>
```

#### Update Profile
```
PUT /api/profiles/profile/update/
PATCH /api/profiles/profile/update/
Authorization: Bearer <access_token>
```

#### Delete Profile
```
DELETE /api/profiles/profile/delete/
Authorization: Bearer <access_token>
```

## Data Models

### User Model (Authentication)
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

### UserProfile Model (Profiles)
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Personal Information
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Fitness Information
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    fitness_goal = models.CharField(
        max_length=50,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('maintenance', 'Maintenance'),
            ('endurance', 'Endurance'),
        ],
        blank=True,
        null=True
    )
    
    # Additional Fields
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Authentication Flow

### 1. User Registration
- Client sends registration data to `/api/auth/register/`
- Server creates user account and returns JWT tokens
- Client stores tokens for future requests

### 2. User Login
- Client sends credentials to `/api/auth/login/`
- Server validates credentials and returns JWT tokens
- Client stores tokens for future requests

### 3. Authenticated Requests
- Client includes `Authorization: Bearer <access_token>` header
- Server validates token and processes request
- When access token expires, use refresh token to get new one

### 4. Token Refresh
- Client sends refresh token to `/api/auth/token/refresh/`
- Server returns new access token
- Client updates stored access token

## Configuration

### Environment Variables
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=zoefit_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOW_ALL_ORIGINS=True
```

### Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Running the Server
```bash
# Development server
python manage.py runserver

# With specific port
python manage.py runserver 8000
```

## Security Features

- **JWT Authentication**: Stateless token-based authentication
- **Password Validation**: Django's built-in password validators
- **Token Blacklisting**: Refresh tokens are blacklisted on logout
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Email Authentication**: Users authenticate with email instead of username

## Error Handling

Standard HTTP status codes:
- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Authentication required/failed
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Dependencies

### Core Django Packages
- `django` - Web framework
- `djangorestframework` - REST API framework
- `django-cors-headers` - CORS handling

### Authentication
- `djangorestframework-simplejwt` - JWT authentication
- `django-environ` - Environment variable management

### Database
- `psycopg2-binary` - PostgreSQL adapter

## Development Guidelines

### Code Organization
- Keep authentication logic separate from business logic
- Use serializers for data validation and serialization
- Implement proper error handling and validation
- Follow Django REST Framework conventions

### API Design
- Use RESTful endpoints with clear naming
- Provide meaningful error messages
- Use HTTP status codes appropriately
- Include helpful documentation in API responses

### Security Best Practices
- Never store passwords in plain text
- Use JWT tokens with proper expiration
- Validate all input data
- Implement proper authentication checks
- Use HTTPS in production

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test profiles

# Run with coverage
python manage.py test --coverage
```

## Deployment Considerations

### Production Settings
- Set `DEBUG = False`
- Configure proper `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Set up proper database connections
- Configure static and media file serving

### Performance Optimization
- Use database indexes for frequently queried fields
- Implement pagination for large datasets
- Cache frequently accessed data
- Optimize database queries

## Future Enhancements

Potential modules to add:
- Workouts tracking
- Nutrition logging
- Progress analytics
- Social features
- AI-powered recommendations
- Workout plans
- Meal planning
