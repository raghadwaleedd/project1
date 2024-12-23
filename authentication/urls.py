from django.urls import path ,re_path
from .views import *
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)




urlpatterns = [
    # Authentication Endpoints
    path('register/', UserRegistrationView.as_view(), name='user_register' ),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    
    # Profile Management
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # JWT Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), 
    
    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'), 
    path('password-change/', PasswordChangeView.as_view(), name='password-change-view'),

]
