from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.renderers import TemplateHTMLRenderer 
from rest_framework.permissions import AllowAny 
from authentication.models import *
# Create your views here.

class MyindexView(APIView): 
    permission_classes = [AllowAny] 
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'fronthtml/index.html'
    
   
    
    def get(self, request): 
        # Count active users
        active_users_count = CustomUser.objects.filter(is_active=True).count()
        
        # Calculate satisfaction rate
        satisfaction_rate = self.calculate_satisfaction_rate() 
        
        context = {
            'active_users_count': active_users_count, 
            'satisfaction_rate': satisfaction_rate,
          }  
        
        return render(request, 'fronthtml/index.html' , context  ) 
    
    
    def calculate_satisfaction_rate(self):
        """Calculate the satisfaction rate based on user ratings. """
        # Get all ratings
        all_ratings = UserRating.objects.all()
        
        # If no ratings exist, return a default value
        if not all_ratings.exists():
            return 95  # Default value when no ratings are available
        
        """  rating__gte=4 is a Django query filter that means "rating greater than or equal to 4"
            gte stands for "greater than or equal to"""
            
        # Calculate the satisfaction rate (ratings of 4 or 5 are considered satisfied)
        total_ratings = all_ratings.count()
        satisfied_ratings = all_ratings.filter(rating__gte=4).count()
        
        # Calculate percentage
        if total_ratings > 0:
            satisfaction_percentage = (satisfied_ratings / total_ratings) * 100
            # Round to the nearest whole number
            satisfaction_percentage = round(satisfaction_percentage)
            return satisfaction_percentage
        
        return 95  # Default in case of division by zero  
      
class login_signup_view(APIView): 
    permission_classes = [AllowAny] 
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'fronthtml/Login_Sign.Html'
  
    def get(self, request):
          return render(request, 'fronthtml/Login_Sign.Html')     
 
 
 
class MysearchView(APIView): 
    permission_classes = [AllowAny] 
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'fronthtml/index2.html'
  
    def get(self, request):
        # Create the response object
        return render(request, 'fronthtml/index2.html')
    