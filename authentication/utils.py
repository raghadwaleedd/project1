import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from typing import Optional , TYPE_CHECKING
import logging


if TYPE_CHECKING:
    from .models import CustomUser as User
else:
    User = get_user_model()


logger = logging.getLogger(__name__)

def generate_email_verification_token(user: User) -> str:
    """
    Generate JWT token for email verification.
    
    Args:
        user (User): User instance to generate token for
        
    Returns:
        str: JWT token encoded as string
        
    Raises:
        jwt.InvalidTokenError: If token generation fails
    """
    try:
        token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.utcnow() + timedelta(days=1),
            'type': 'email_verification'
        }, settings.SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        logger.error(f"Failed to generate verification token for {user.email}: {str(e)}")
        raise 
    
    
def generate_password_reset_token(user: User) -> str:
    """
    Generate JWT token for password reset.
    
    Args:
        user (User): User instance to generate token for
        
    Returns:
        str: JWT token encoded as string
        
    Raises:
        jwt.InvalidTokenError: If token generation fails
    """ 
    try:
        token = jwt.encode({
            'user_id': str(user.id),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'type': 'password_reset'
        }, settings.SECRET_KEY, algorithm='HS256')
        logger.info(f"Generated password reset token for {user.email}")
        return token
    except Exception as e:
        logger.error(f"Failed to generate password reset token for {user.email}: {str(e)}")
        raise
 
 
 
def send_verification_email(user: User, request) -> bool:
    """
    Send verification email to user.
    
    Args:
        user (User): User to send verification email to
        request: HTTP request object for building URLs
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Raises:
        Exception: If email sending fails
    """
    try:
        token = generate_email_verification_token(user)
        verification_url = f"{request.scheme}://{request.get_host()}/api/auth/verify-email/{token}"
        
        context = {
            'user': user,
            'verification_url': verification_url,
            'expiry_hours': 24  # Match token expiry
        }
        
        html_message = render_to_string('email/verification_email.html', context)
        plain_message = render_to_string('email/verification_email.txt', context)
        
        send_mail(
            subject='Verify your email address',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        raise

def send_password_reset_email(user: User, request) -> bool:
    """
    Send password reset email to user.
    
    Args:
        user (User): User to send password reset email to
        request: HTTP request object for building URLs
        
    Returns:
        bool: True if email sent successfully, False otherwise
        
    Raises:
        Exception: If email sending fails
    """
    try:
        token = generate_password_reset_token(user)
        reset_url = f"{request.scheme}://{request.get_host()}/api/auth/reset-password/{token}"
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'expiry_hours': 1  # Match token expiry
        }
        
        html_message = render_to_string('email/password_reset_email.html', context)
        plain_message = render_to_string('email/password_reset_email.txt', context)
        
        send_mail(
            subject='Reset your password',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        raise