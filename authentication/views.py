from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny
from social_django.utils import load_strategy, load_backend
from social_core.backends.google import GoogleOAuth2
from social_core.exceptions import MissingBackend, AuthTokenError
from requests.exceptions import HTTPError
from . serializer import * 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle  
import jwt 
import logging 
from .utils import * 



class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
        
                'id': user.id,
                'username': user.username,
                'email': user.email ,
                'refresh': str(refresh),
                'access': str(refresh.access_token) 
                
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)

            # Check for account lockout first
            if user.check_account_locked():
                return Response({
                    'error': 'Account is temporarily locked. Please try again later.'
                }, status=status.HTTP_403_FORBIDDEN)

            # Authenticate user
            authenticated_user = authenticate(request, email=email, password=password)

            if authenticated_user:
                # Reset failed login attempts on successful login
                user.failed_login_attempts = 0
                user.save(update_fields=['failed_login_attempts'])

                # Generate JWT tokens
                refresh = RefreshToken.for_user(authenticated_user)
                return Response({
                    'username': authenticated_user.username,
                    'email': authenticated_user.email,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                })
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                
                # Lock account after 5 consecutive failed attempts
                if user.failed_login_attempts >= 5:
                    user.lock_account()
                
                user.save(update_fields=['failed_login_attempts'])
                
                return Response({
                    'error': 'the password is wrong . Account will be locked after {} more failed attempts.'.format(5 - user.failed_login_attempts)
                }, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({
                'error': 'the email DoesNotExist  '
            }, status=status.HTTP_401_UNAUTHORIZED)
  

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Blacklist the refresh token
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
 
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            
            if payload['type'] != 'email_verification':
                return Response({'error': 'Invalid token type'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
                logger.info(f"Email verified for user {user.email}")
            
            return Response({'message': 'Email successfully verified'})
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired verification token used")
            return Response({'error': 'Verification link has expired'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            logger.warning(f"Invalid verification token used")
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'success': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@throttle_classes([AnonRateThrottle])
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(email=serializer.validated_data['email'])
                send_password_reset_email(user, request)
                logger.info(f"Password reset requested for {user.email}")
                return Response({'message': 'Password reset email has been sent'})
            except User.DoesNotExist:
                logger.warning(f"Password reset attempted for non-existent email")
                # Return success even if email doesn't exist for security
                return Response({'message': 'Password reset email has been sent'})
            except Exception as e:
                logger.error(f"Password reset email failed: {str(e)}")
                return Response({'error': 'Failed to send reset email'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            
            if payload['type'] != 'password_reset':
                return Response({'error': 'Invalid token type'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            serializer = PasswordResetConfirmSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(serializer.validated_data['password'])
                user.save()
                logger.info(f"Password reset successful for {user.email}")
                return Response({'message': 'Password has been reset'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired password reset token used")
            return Response({'error': 'Reset link has expired'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            logger.warning(f"Invalid password reset token used")
            return Response({'error': 'Invalid token'}, 
                          status=status.HTTP_400_BAD_REQUEST)