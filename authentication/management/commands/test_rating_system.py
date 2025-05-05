# yourapp/management/commands/test_rating_system.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from authentication.models import UserRating

class Command(BaseCommand):
    help = 'Test the rating system by creating test users and ratings'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create test users with different scenarios
        self.stdout.write('Creating test users...')
        
        # 1. New user who can rate (account older than 6 months, no ratings)
        new_eligible_user = User.objects.create_user(
            username='new_eligible',  # Add username parameter
            email='new_eligible@example.com',
            password='password123',
            date_joined=timezone.now() - timedelta(days=200)
        )
        
        # 2. User who rated recently (cannot rate again)
        recent_rater = User.objects.create_user(
            username='recent_rater',  # Add username parameter
            email='recent_rater@example.com',
            password='password123',
            date_joined=timezone.now() - timedelta(days=200)
        )
        UserRating.objects.create(
            user=recent_rater,
            rating=4,
            feedback='This is a recent rating'
        )
        
        # 3. User who rated long ago (can rate again)
        old_rater = User.objects.create_user(
            username='old_rater',  # Add username parameter
            email='old_rater@example.com',
            password='password123',
            date_joined=timezone.now() - timedelta(days=400)
        )
        old_rating = UserRating.objects.create(
            user=old_rater,
            rating=3,
            feedback='This is an old rating'
        )
        # Set creation date to 7 months ago
        old_date = timezone.now() - timedelta(days=210)
        UserRating.objects.filter(pk=old_rating.pk).update(created_at=old_date)
        
        # 4. User with too new account (cannot rate yet)
        new_account = User.objects.create_user(
            username='new_account',  # Add username parameter
            email='new_account@example.com',
            password='password123',
            date_joined=timezone.now() - timedelta(days=30)
        )
        
        # Test the can_user_rate_again method for each user
        self.stdout.write('\nTesting can_user_rate_again method:')
        self.stdout.write(f'New eligible user: {UserRating.can_user_rate_again(new_eligible_user)}')
        self.stdout.write(f'Recent rater: {UserRating.can_user_rate_again(recent_rater)}')
        self.stdout.write(f'Old rater: {UserRating.can_user_rate_again(old_rater)}')
        self.stdout.write(f'New account: {UserRating.can_user_rate_again(new_account)}')
        
        self.stdout.write(self.style.SUCCESS('\nTest users created successfully!'))
        self.stdout.write('\nTest credentials:')
        self.stdout.write('  - New eligible user: new_eligible@example.com / password123')
        self.stdout.write('  - Recent rater: recent_rater@example.com / password123')
        self.stdout.write('  - Old rater: old_rater@example.com / password123')
        self.stdout.write('  - New account: new_account@example.com / password123')
        
        self.stdout.write('\nTo test the frontend:')
        self.stdout.write('1. Log in with one of these users')
        self.stdout.write('2. Visit /test-rating/ to test the popup manually')
        self.stdout.write('3. Or navigate to any page to see if the popup appears automatically')