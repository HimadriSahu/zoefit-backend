# Environment Setup Guide

## Development Environment Setup

1. **Activate Virtual Environment**
   ```bash
   cd back
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source venv/bin/activate     # Linux/Mac
   ```

2. **Install Dependencies**
   ```bash
   cd zoefit
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Update with your local settings
   - Ensure database credentials are correct

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Production Environment Setup

1. **Environment Variables**
   - Copy `.env.production` to `.env`
   - Update with production values
   - Generate a secure SECRET_KEY

2. **Security Checklist**
   - Set `DEBUG=False`
   - Configure `ALLOWED_HOSTS`
   - Set up SSL certificate
   - Configure email backend
   - Set up database with proper credentials

3. **Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Database Migrations**
   ```bash
   python manage.py migrate
   ```

## Environment-Specific Settings

### Development (.env)
- `DEBUG=True`
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- `CORS_ALLOW_ALL_ORIGINS=True`
- Console email backend

### Production (.env)
- `DEBUG=False`
- `ALLOWED_HOSTS=yourdomain.com`
- `CORS_ALLOWED_ORIGINS=https://yourdomain.com`
- SMTP email backend
- SSL/HTTPS enabled

## Security Best Practices

1. **Never commit `.env` files to version control**
2. **Use strong, unique SECRET_KEY**
3. **Enable HTTPS in production**
4. **Restrict CORS origins**
5. **Use environment-specific database credentials**
6. **Regular security updates**
