from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    api_root_view,
    register_view,
    login_view,
    profile_view,
    update_profile_view,
    logout_view,
    forgot_password_view,
    change_password_view
)

app_name = 'authentication'

urlpatterns = [
    # API Root
    path('', api_root_view, name='api_root'),
    
    # Registration and Login
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('logout/', logout_view, name='logout'),
    
    # Token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    path('change-password/', change_password_view, name='change_password'),
]

