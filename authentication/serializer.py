from . models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ 
from rest_framework.validators import UniqueValidator


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password] ,
        style={'input_type': 'password'}  ,
        
    )
    password2 = serializers.CharField( 
        write_only=True,
        required=True ,
        style={'input_type': 'password'} , 
       
    )
    
    email= serializers.EmailField(required=True ,
          )
    
    first_name= serializers.CharField(required=True )
    last_name= serializers.CharField(required=True )  
    
    username = serializers.CharField(
        required=False,
        
    )
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',  
            'email', 
            'password', 
            'password2',   
            'username', 
                    
        ] 
       
         
         
    def validate_email(self, value):
        """Validate email is unique and properly formatted."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value.lower()   
     
     
    def validate(self, attrs):
        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            ) 
            
             
         # Validate that first_name and last_name are not empty
        if not attrs.get('first_name'):
            raise serializers.ValidationError(
                {"first_name": "First name is required."}
            )
        
        if not attrs.get('last_name'):
            raise serializers.ValidationError(
                {"last_name": "Last name is required."}
            ) 
            
        
            
            
        return attrs
    
    
    
    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop('password2') 
        
        username = validated_data.pop('username', None)
        if not username:
            username = f"{validated_data['first_name']} {validated_data['last_name']}"
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            username=username,
            password=validated_data['password'] ,
            first_name= validated_data["first_name"] ,
            last_name= validated_data["last_name"]
        )
        
       
        
        return user



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField( 
      write_only=True , 
      style={'input_type': 'password'}  )  
    
    def validate_email(self, value):
        """Convert email to lowercase for consistency."""
        return value.lower()



class UserProfileSerializer(serializers.ModelSerializer): 
    
    subscription_status = serializers.SerializerMethodField()
    remaining_searches = serializers.SerializerMethodField() 
    
    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'username', 
            'first_name', 
            'last_name',  
            'profile_picture',
            'date_of_birth',
            'is_premium', 
            'subscription_start',
            'subscription_end',
            'plan_type',
            'role',
            'preferred_language',
            'preferred_theme',  
            'last_activity',
            'search_count',
            'daily_search_limit',
            'subscription_status',
            'remaining_searches',
            'is_verified',
            'auth_provider'
        ]
        
        read_only_fields = [ 
            'id', 
            'email', 
            'is_premium',
            'subscription_start',
            'subscription_end',
            'search_count',
            'last_activity',
            'is_verified',
            'auth_provider'                 
                            
              ]  
    def get_subscription_status(self, obj):
        """Get the current subscription status."""
        return {
            'is_active': obj.is_active_subscription(),
            'days_remaining': obj.get_subscription_days_remaining()
        }

    def get_remaining_searches(self, obj):
        """Get remaining daily searches."""
        return max(0, obj.daily_search_limit - obj.search_count)




class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": _("Password fields didn't match.")}
            )
        return attrs 
    
           
class PasswordResetRequestSerializer(serializers.Serializer): 
    """ This serializer handles the initial request to reset a password, where the user provides their email. It is commonly used in "Forgot Password" .
        Key Methods and Validations:

        validate_email: Verifies that a user account exists with the specified email.
        This serializer doesn’t directly reset the password; instead, it triggers a password reset process (e.g., sending a reset link with a token to the email). """ 
        
    email = serializers.EmailField()  
    
    def validate_email(self, value):
        """Verify that user exists with this email."""
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(_("No user found with this email address."))
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer): 
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password] ,
        style={'input_type': 'password'}
    ) 
    
    password2 = serializers.CharField(write_only=True ,  style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs       
        
        
class UserSettingsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'preferred_language',
            'preferred_theme',
            'notifications_enabled',
            'daily_search_limit'
        ]
        read_only_fields = ['daily_search_limit']