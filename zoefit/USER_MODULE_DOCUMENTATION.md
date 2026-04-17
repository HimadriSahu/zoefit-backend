# User Module Documentation

## Overview

The User Module in ZoeFit is split into two distinct components:
1. **Authentication Module** - Handles user registration, login, and authentication
2. **Profiles Module** - Manages user profile information and fitness data

This separation ensures clean architecture and maintains the single responsibility principle.

## Authentication Module

### Purpose
Handles user authentication, authorization, and session management using JWT tokens.

### Key Features
- Email-based authentication
- JWT token generation and validation
- Password management (reset, change)
- User registration and login
- Token refresh and blacklisting

### Models

#### User Model
```python
class User(AbstractUser):
    """
    Custom User model for authentication only.
    Contains minimal fields required for login and identification.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
```

**Fields:**
- `email`: Unique email address used for login
- `username`: Display username (required but not used for login)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Serializers

#### UserRegistrationSerializer
Handles user registration with password validation.

**Input Fields:**
- `username` (required)
- `email` (required, unique)
- `password` (required, validated)
- `password2` (required, must match password)

**Validation:**
- Password strength validation using Django's built-in validators
- Password confirmation matching
- Email uniqueness check
- Username uniqueness check

#### UserLoginSerializer
Handles user authentication and login.

**Input Fields:**
- `email` (required)
- `password` (required)

**Process:**
- Validates email and password
- Uses custom EmailBackend for authentication
- Returns authenticated user object for token generation

### Views

#### Registration View (`/api/auth/register/`)
```python
POST /api/auth/register/
```
- Creates new user account
- Generates JWT tokens (access + refresh)
- Returns user info and tokens

**Response:**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username"
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

#### Login View (`/api/auth/login/`)
```python
POST /api/auth/login/
```
- Authenticates user credentials
- Generates JWT tokens
- Returns user info and tokens

#### Logout View (`/api/auth/logout/`)
```python
POST /api/auth/logout/
Authorization: Bearer <access_token>
```
- Blacklists refresh token
- Prevents token reuse
- Requires authentication

#### Password Management Views
- `POST /api/auth/forgot-password/` - Password reset request
- `POST /api/auth/change-password/` - Password change (authenticated)

### Custom Authentication Backend

#### EmailBackend
```python
class EmailBackend(BaseBackend):
    """
    Custom authentication backend that allows users to login with email
    instead of username.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        # Authenticates user using email and password
        # Falls back to username if email not found
```

**Features:**
- Email-first authentication
- Username fallback support
- Secure password verification
- User object retrieval

## Profiles Module

### Purpose
Manages user profile information, fitness data, and personal details separate from authentication.

### Key Features
- Personal information management
- Fitness goal tracking
- Profile picture uploads
- CRUD operations for profile data
- One-to-one relationship with User model

### Models

#### UserProfile Model
```python
class UserProfile(models.Model):
    """
    Extended user profile containing personal and fitness information.
    One-to-one relationship with User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Fitness Information
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
    fitness_goal = models.CharField(max_length=50, choices=FITNESS_GOALS, blank=True, null=True)
    
    # Additional Fields
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Field Categories:**

**Personal Information:**
- `first_name`: User's first name
- `last_name`: User's last name
- `phone_number`: Contact phone number
- `date_of_birth`: Birth date
- `profile_picture`: Profile image file

**Fitness Information:**
- `height`: Height in centimeters
- `weight`: Weight in kilograms
- `fitness_goal`: Fitness objective (weight_loss, muscle_gain, maintenance, endurance)

**Additional Information:**
- `bio`: User biography/description
- `location`: User's location

**Properties:**
- `full_name`: Computed property returning full name

### Serializers

#### UserProfileSerializer
Handles serialization of user profile data for API responses.

**Fields:**
- All UserProfile model fields
- `full_name` (read-only computed property)

**Read-only Fields:**
- `id`, `created_at`, `updated_at`

#### UserProfileCreateSerializer
Handles profile creation with all fields optional.

**Features:**
- All fields are optional during creation
- Validates data types and formats
- Handles file uploads for profile pictures

### Views

#### Create Profile View (`/api/profiles/profile/create/`)
```python
POST /api/profiles/profile/create/
Authorization: Bearer <access_token>
```
- Creates new profile for authenticated user
- Prevents duplicate profile creation
- Returns created profile data

**Validation:**
- Checks if profile already exists
- Validates all input data
- Handles file uploads

#### Get Profile View (`/api/profiles/profile/`)
```python
GET /api/profiles/profile/
Authorization: Bearer <access_token>
```
- Retrieves current user's profile
- Returns 404 if profile doesn't exist
- Includes all profile fields

#### Update Profile View (`/api/profiles/profile/update/`)
```python
PUT /api/profiles/profile/update/
PATCH /api/profiles/profile/update/
Authorization: Bearer <access_token>
```
- Updates existing profile
- Supports both PUT (full update) and PATCH (partial update)
- Validates all input data
- Returns updated profile

#### Delete Profile View (`/api/profiles/profile/delete/`)
```python
DELETE /api/profiles/profile/delete/
Authorization: Bearer <access_token>
```
- Deletes user's profile
- Requires authentication
- Returns success message

## User Workflow

### 1. Registration Process
```
1. User submits registration data (username, email, password, password2)
2. System validates data and creates User account
3. JWT tokens are generated and returned
4. User can now authenticate with tokens
```

### 2. Profile Creation Process
```
1. User authenticates with JWT token
2. User submits profile data (optional fields)
3. System creates UserProfile linked to User
4. Profile data is stored and returned
```

### 3. Authentication Flow
```
1. User logs in with email/password
2. System validates credentials
3. JWT tokens are generated
4. Access token used for authenticated requests
5. Refresh token used to get new access tokens
```

### 4. Profile Management
```
1. User authenticates with access token
2. User can view, update, or delete profile
3. All profile operations require authentication
4. Profile data is separate from authentication data
```

## Security Considerations

### Authentication Security
- **Password Validation**: Uses Django's built-in password validators
- **JWT Tokens**: Secure token-based authentication
- **Token Blacklisting**: Prevents token reuse after logout
- **Email Authentication**: More secure than username-only login

### Profile Security
- **Authentication Required**: All profile operations need valid JWT token
- **User Isolation**: Users can only access their own profiles
- **Data Validation**: All input data is validated before storage
- **File Upload Security**: Profile pictures are validated and stored securely

### Data Protection
- **Separation of Concerns**: Authentication data separate from profile data
- **Minimal Data Collection**: Only collect necessary user information
- **Secure Storage**: Sensitive data is properly secured
- **Access Control**: Proper authorization checks on all endpoints

## API Usage Examples

### Registration and Profile Setup
```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'

# 2. Create profile (using returned access token)
curl -X POST http://localhost:8000/api/profiles/profile/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "height": 175.5,
    "weight": 70.0,
    "fitness_goal": "muscle_gain"
  }'
```

### Login and Profile Access
```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'

# 2. Get profile
curl -X GET http://localhost:8000/api/profiles/profile/ \
  -H "Authorization: Bearer <access_token>"
```

## Error Handling

### Authentication Errors
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid credentials or missing token
- `404 Not Found`: User not found (for password reset)

### Profile Errors
- `400 Bad Request`: Invalid profile data or profile already exists
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Profile doesn't exist

### Common Error Responses
```json
{
    "error": "Invalid credentials",
    "detail": "Email or password is incorrect"
}

{
    "error": "Profile already exists",
    "detail": "Use update endpoint instead"
}
```

## Database Relationships

### User-Profile Relationship
```
User (1) -----> (1) UserProfile
- One-to-one relationship
- User can have at most one profile
- Profile must have exactly one user
- Cascade delete: Profile deleted when User deleted
```

### Foreign Key Constraints
- `UserProfile.user` → `User.id` (One-to-One)
- `on_delete=models.CASCADE` - Profile deleted if user deleted
- `related_name='profile'` - Access profile via `user.profile`

## Testing

### Authentication Tests
```python
# Test user registration
def test_user_registration():
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'password2': 'TestPass123!'
    }
    response = client.post('/api/auth/register/', data)
    assert response.status_code == 201

# Test user login
def test_user_login():
    response = client.post('/api/auth/login/', {
        'email': 'test@example.com',
        'password': 'TestPass123!'
    })
    assert response.status_code == 200
```

### Profile Tests
```python
# Test profile creation
def test_profile_creation():
    client.force_authenticate(user=user)
    response = client.post('/api/profiles/profile/create/', {
        'first_name': 'John',
        'last_name': 'Doe'
    })
    assert response.status_code == 201

# Test profile retrieval
def test_profile_retrieval():
    client.force_authenticate(user=user)
    response = client.get('/api/profiles/profile/')
    assert response.status_code == 200
```

## Best Practices

### Development Guidelines
1. **Always validate input data** before processing
2. **Use authentication decorators** on protected endpoints
3. **Handle errors gracefully** with meaningful messages
4. **Separate concerns** between authentication and business logic
5. **Use proper HTTP status codes** for different scenarios

### Security Best Practices
1. **Never store passwords in plain text**
2. **Use JWT tokens with proper expiration**
3. **Validate all user input**
4. **Implement proper access controls**
5. **Use HTTPS in production**

### Code Organization
1. **Keep models focused** on single responsibility
2. **Use serializers for data validation**
3. **Implement proper error handling**
4. **Write comprehensive tests**
5. **Document API endpoints clearly**

## Future Enhancements

### Potential Features
- **Social Login Integration** (Google, Facebook, etc.)
- **Two-Factor Authentication**
- **Email Verification**
- **Profile Privacy Settings**
- **Profile Completion Tracking**
- **Avatar Management System**
- **Profile Templates**
- **Social Features** (following, friends)

### Scalability Considerations
- **Database Indexing** for frequently queried fields
- **Caching Strategy** for profile data
- **File Storage Optimization** for profile pictures
- **API Rate Limiting** for profile operations
- **Data Analytics** for profile usage patterns
