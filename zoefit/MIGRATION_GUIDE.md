# Database Migration Guide

This guide will help you set up the database and run migrations for the ZoeFit backend.

## Prerequisites

1. PostgreSQL must be installed and running
2. Database `zoefit_db` should be created (or update settings.py with your database name)
3. Virtual environment should be activated

## Database Setup

### 1. Create PostgreSQL Database

If you haven't created the database yet, connect to PostgreSQL and run:

```sql
CREATE DATABASE zoefit_db;
```

Or using command line:
```bash
createdb zoefit_db
```

### 2. Update Database Credentials (if needed)

Edit `zoefit/settings.py` and update the database configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'zoefit_db',  # Your database name
        'USER': 'postgres',    # Your PostgreSQL username
        'PASSWORD': 'your_password',  # Your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Running Migrations

### Step 1: Create Migrations

Navigate to the project directory:
```bash
cd back/zoefit
```

Create migrations for all apps:
```bash
python manage.py makemigrations
```

This will create migration files for:
- Django's built-in apps (admin, auth, sessions, etc.)
- Authentication module (User model)
- Token blacklist (for JWT logout functionality)

### Step 2: Apply Migrations

Apply all migrations to create database tables:
```bash
python manage.py migrate
```

This will create all necessary tables including:
- `users` table (custom User model)
- `authtoken_tokenblacklist` tables (for JWT token blacklisting)
- Django's default tables (admin, sessions, etc.)

### Step 3: Create Superuser (Optional)

Create an admin user to access Django admin panel:
```bash
python manage.py createsuperuser
```

Follow the prompts to set email, username, and password.

## Verify Setup

### Check Database Tables

You can verify the tables were created by connecting to PostgreSQL:
```sql
\c zoefit_db
\dt
```

You should see tables like:
- `users`
- `authtoken_tokenblacklist_*`
- `django_*` (various Django tables)

### Test the API

Start the development server:
```bash
python manage.py runserver
```

Test the registration endpoint:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "password2": "TestPass123!"
  }'
```

## Troubleshooting

### Migration Errors

If you encounter migration errors:

1. **Database connection issues:**
   - Verify PostgreSQL is running
   - Check database credentials in settings.py
   - Ensure database exists

2. **Migration conflicts:**
   - If you have existing migrations, you may need to reset:
     ```bash
     python manage.py migrate --run-syncdb
     ```

3. **Custom User model issues:**
   - Ensure `AUTH_USER_MODEL = 'authentication.User'` is set in settings.py
   - Delete old migrations if switching from default User model (be careful!)

### Common Issues

- **"relation does not exist"**: Run migrations again
- **"permission denied"**: Check PostgreSQL user permissions
- **"database does not exist"**: Create the database first

## Next Steps

After successful migration:
1. Test authentication endpoints
2. Create test users
3. Integrate with Expo Go frontend
4. Add additional modules as needed

