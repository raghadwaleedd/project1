# tests.py
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import UserRating ,CustomUser


class UserRatingModelTests(TestCase):
    def setUp(self):
        # Create a test user - added username parameter
        self.user = CustomUser.objects.create_user(
            username='testuser',  # Add username parameter
            email='testuser@example.com',
            password='testpass123',
            date_joined=timezone.now() - timedelta(days=200)  # Joined more than 6 months ago
        )
    
    def test_can_user_rate_again_new_user(self):
        """Test that a user with no ratings can rate"""
        self.assertTrue(UserRating.can_user_rate_again(self.user))
    
    def test_can_user_rate_again_recent_rating(self):
        """Test that a user who rated recently cannot rate again"""
        # Create a recent rating
        UserRating.objects.create(user=self.user, rating=5, feedback="Great service!")
        self.assertFalse(UserRating.can_user_rate_again(self.user))
    
    def test_can_user_rate_again_old_rating(self):
        """Test that a user who rated more than 6 months ago can rate again"""
        # Create an old rating
        old_rating = UserRating.objects.create(user=self.user, rating=3, feedback="It's okay")
        # Manually set the creation date to more than 6 months ago
        old_date = timezone.now() - timedelta(days=190)
        UserRating.objects.filter(pk=old_rating.pk).update(created_at=old_date)
        
        # Refresh from database
        old_rating.refresh_from_db()
        
        # Now test
        self.assertTrue(UserRating.can_user_rate_again(self.user))
    
    def test_account_too_new(self):
        """Test that a user with a new account cannot rate"""
        new_user = CustomUser.objects.create_user(
            username='newuser',  # Add username parameter
            email='newuser@example.com',
            password='newpass123',
            date_joined=timezone.now() - timedelta(days=30)  # Joined less than 6 months ago
        )
        self.assertFalse(UserRating.can_user_rate_again(new_user))

class UserRatingAPITests(TestCase):
    def setUp(self):
        # Create a test user - added username parameter
        self.user = CustomUser.objects.create_user(
            username='testuser',  # Add username parameter
            email='testuser@example.com',
            password='testpass123',
            date_joined=timezone.now() - timedelta(days=200)  # Joined more than 6 months ago
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Define URLs
        self.status_url = reverse('rating_status')  # Make sure this matches your URL name
        self.submit_url = reverse('submit_rating')  # Make sure this matches your URL name
    
    def test_rating_status_api(self):
        """Test the rating status API returns correct information"""
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_rate'])
        self.assertTrue(response.data['should_show_popup'])
        self.assertIsNone(response.data['last_rating_date'])
    
    def test_submit_rating_api_success(self):
        """Test submitting a rating successfully"""
        data = {
            'rating': 4,
            'feedback': 'This is a test feedback'
        }
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the rating was created
        self.assertEqual(UserRating.objects.count(), 1)
        rating = UserRating.objects.first()
        self.assertEqual(rating.rating, 4)
        self.assertEqual(rating.feedback, 'This is a test feedback')
    
    def test_submit_rating_api_validation(self):
        """Test validation prevents invalid ratings"""
        # Test missing rating
        data = {
            'feedback': 'Missing rating'
        }
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid rating value
        data = {
            'rating': 6,  # Should be 1-5
            'feedback': 'Invalid rating'
        }
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test too many words in feedback
        long_feedback = ' '.join(['word'] * 101)  # 101 words
        data = {
            'rating': 3,
            'feedback': long_feedback
        }
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_submit_twice(self):
        """Test that a user cannot submit twice within 6 months"""
        # First submission
        data = {
            'rating': 4,
            'feedback': 'First submission'
        }
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Second submission
        data = {
            'rating': 5,
            'feedback': 'Second submission'
        }
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
