# Using the Custom User Model

Since we're using a custom User model (`AUTH_USER_MODEL = 'authentication.User'`), you **cannot** import Django's default User model.

## ❌ Wrong Way

```python
from django.contrib.auth.models import User  # This will cause an error!
User.objects.all()
```

**Error:** `AttributeError: Manager isn't available; 'auth.User' has been swapped for 'authentication.User'`

## ✅ Correct Ways

### Option 1: Import from your authentication app (Recommended)

```python
from authentication.models import User
User.objects.all()
```

### Option 2: Use Django's get_user_model() (Best Practice)

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.all()
```

### Option 3: Direct import with full path

```python
from authentication.models import User
```

## Examples in Django Shell

```python
# Start Django shell
python manage.py shell

# Import the custom User model
from django.contrib.auth import get_user_model
User = get_user_model()

# Now you can use it
User.objects.all()
User.objects.create_user(
    email='test@example.com',
    username='testuser',
    password='testpass123'
)

# Or import directly
from authentication.models import User
users = User.objects.all()
```

## Why This Happens

When you set `AUTH_USER_MODEL = 'authentication.User'` in settings.py, Django replaces the default User model with your custom one. The old `django.contrib.auth.models.User` is no longer available.

## In Your Code

Always use `get_user_model()` in your code to ensure compatibility:

```python
# In views.py, serializers.py, etc.
from django.contrib.auth import get_user_model

User = get_user_model()

# Now use User normally
user = User.objects.get(email='test@example.com')
```

