from django.db import models 
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin , AbstractUser)   

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from rest_framework_simplejwt.tokens import RefreshToken 
from datetime import timedelta



AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'} 



class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of username.
    """
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        # Set default values for custom fields
        user.auth_provider = user.auth_provider or 'email'
        user.plan_type = user.plan_type or 'basic'
        user.role = user.role or 'user'
        user.preferred_language = user.preferred_language or 'en'
        user.preferred_theme = user.preferred_theme or 'light'
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

    

class CustomUser(AbstractUser):  
    objects = CustomUserManager() 
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        unique=True,
        verbose_name=_('email address'),
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    ) 
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/',  # Organized by year/month
        null=True,
        blank=True
    )
    
    
    # Subscription and premium status
    is_premium = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(auto_now_add=True ,null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True) 
    
    
    auth_provider = models.CharField(
    max_length=255, 
    blank=False, 
    null=False, 
    default=AUTH_PROVIDERS.get('email')
    )
    
    PLAN_CHOICES = [
        ('basic', _('Basic')),
        ('premium', _('Premium')),
        ('enterprise', _('Enterprise')),
    ] 
    
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='basic'
    )

    # Role: For managing different access levels (e.g., Admin, User)
    ROLE_CHOICES = [
        ('user', _('User')),
        ('admin', _('Admin')),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )
    
    

    # Language/Settings
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('es', _('Spanish')),
        ('fr', _('French')),
        
    ]
    preferred_language = models.CharField(
        max_length=50,
        choices=LANGUAGE_CHOICES,
        default='en'
    ) 
    
    THEME_CHOICES = [
        ('light', _('Light')),
        ('dark', _('Dark')),
        ('system', _('System')),  
    ]
    preferred_theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )
    



    
    is_verified = models.BooleanField(default=False) #Tracks whether user has completed email verification 
    last_login_ip = models.GenericIPAddressField(null=True, blank=True) #Stores IP address of user's most recent login 
    registration_ip = models.GenericIPAddressField(null=True, blank=True)  # Captures IP address when user initially registers
    failed_login_attempts = models.PositiveIntegerField(default=0)  # Added login attempts tracking
    
    
    
    api_key = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    is_account_locked = models.BooleanField(default=False, null=True, blank=True)



    # Add related_name to avoid conflicts with Django's auth.User model
    groups = models.ManyToManyField('auth.Group', related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_permissions', blank=True)
    

    # Override username to use email as primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return f"{self.email} ({self.get_full_name() or self.username})"

    def lock_account(self):
        """Lock the user's account."""
        self.is_account_locked = True
        self.save(update_fields=['is_account_locked'])  
        
    def unlock_account(self):
        """Unlock the user's account."""
        self.is_account_locked = False
        self.failed_login_attempts = 0
        self.save(update_fields=['is_account_locked', 'failed_login_attempts']) 
        
    
    def check_account_locked(self):
        """Check if the account is locked."""
        return self.is_account_locked 
         
    
        
        
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),

        ]



      
    @property
    def full_name(self):
        """Return the full name, with a fallback to username."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username



