# Quick Start Guide - ZoeFit Backend

## Prerequisites Checklist
- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and running
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

## Setup Steps

### 1. Database Setup
```bash
# Create PostgreSQL database
createdb zoefit_db

# Or using psql:
psql -U postgres
CREATE DATABASE zoefit_db;
```

### 2. Update Database Credentials (if needed)
Edit `zoefit/settings.py` and update:
- Database name
- Username
- Password

### 3. Run Migrations
```bash
cd back/zoefit
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Start Server
```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

## Test Authentication

### Register a User
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

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### Get Profile (with token)
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login user |
| POST | `/api/auth/logout/` | Yes | Logout (blacklist token) |
| POST | `/api/auth/token/refresh/` | No | Refresh access token |
| GET | `/api/auth/profile/` | Yes | Get user profile |
| PUT/PATCH | `/api/auth/profile/update/` | Yes | Update profile |
| POST | `/api/auth/change-password/` | Yes | Change password |

## Project Structure

```
back/zoefit/
├── authentication/     # Authentication module (READY)
├── api/                # Reserved for future modules
├── zoefit/             # Project settings
└── requirements.txt    # Dependencies
```

## Next Steps

1. ✅ Authentication module is ready
2. ⏭️ Test all endpoints
3. ⏭️ Integrate with Expo Go frontend
4. ⏭️ Add additional modules (workouts, nutrition, AI, etc.)

## Documentation

- `SETUP.md` - Detailed setup instructions
- `MIGRATION_GUIDE.md` - Database migration guide
- `AUTHENTICATION_MODULE_SUMMARY.md` - Complete module summary
- `authentication/README.md` - API endpoint documentation

## Troubleshooting

**Database connection error?**
- Check PostgreSQL is running
- Verify credentials in `settings.py`
- Ensure database exists

**Migration errors?**
- See `MIGRATION_GUIDE.md` for detailed troubleshooting

**Import errors?**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

## Support

For detailed information, see:
- `SETUP.md` - Full setup guide
- `MIGRATION_GUIDE.md` - Database setup
- `authentication/README.md` - API documentation

