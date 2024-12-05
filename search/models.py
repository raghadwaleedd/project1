from django.db import models
from django.utils import timezone
from authentication.models import CustomUser 
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid

 

class InputType(models.TextChoices):
    TEXT = 'TEXT', 'Text'
    AUDIO = 'AUDIO', 'Audio'
    IMAGE = 'IMAGE', 'Image'
    FILE = 'FILE', 'File'

class OutputType(models.TextChoices):
    TEXT = 'TEXT', 'Text'
    AUDIO = 'AUDIO', 'Audio'
    IMAGE = 'IMAGE', 'Image'
    FILE = 'FILE', 'File'  
    
    
class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )  
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    
    title = models.CharField(max_length=255, null=True, blank=True)  
    
    is_active = models.BooleanField(default=True)  
    is_archived = models.BooleanField(default=False)    
      
    query_count = models.PositiveIntegerField(default=0) 
    
    
    class Meta:
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_active', 'created_at'])
        ] 
        
        
    def save_with_title(self, title=None):
        """
        Save the session with an optional title.
        If no title is provided, generate a default one.
        """
        if not title:
            # Generate a title based on the first search query if available
            first_search = self.searches.order_by('query_time').first()
            title = first_search.query_text[:50] if first_search else f"Chat Session {self.id}"
        
        self.title = title
        self.save()
        return self  
    
    
    def add_query(self):
        """Increment the query count for this session."""
        self.query_count += 1
        if self.query_count >= 20:  # End the session if the limit is reached
            self.is_active = False
        self.save()  
        
        
        
    def end_session(self):
        """
        Mark the session as inactive when the user wants to start a new chat.
        """
        self.is_active = False 
        self.is_archived = True
        self.save()
        return self  
    
    
    
    def __str__(self):
        return f"Session {self.id} for {self.user.email}"  
    
    
    
class Search(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_searches"
    ) 
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="session_searches"  
        
        ) 
    
    input_type = models.CharField(
        max_length=10, 
        choices=InputType.choices, 
        default=InputType.TEXT
    ) 
    
    output_type = models.CharField(
        max_length=10, 
        choices=OutputType.choices, 
        default=OutputType.TEXT
    )
    
    query_text = models.TextField(null=True, blank=True) 
    response_text = models.TextField(null=True, blank=True)  # Full LLM response text
   
    
    query_time = models.DateTimeField(auto_now_add=True)  # Timestamp for each search 
    response_time = models.DurationField(null=True, blank=True)  # Time taken to generate response

    class Meta: 
        
        ordering = ["-query_time"] 
        unique_together = [["user", "query_text" ]] 
        
        indexes = [  # Use models.Index to define custom indexes
            models.Index(fields=["user", "query_time"]), 
            models.Index(fields=['session', 'query_time']) 
        ] 
        
        verbose_name = "User Search"
        verbose_name_plural = "User Searches"
        db_table = "user_searches" 
        
        constraints = [            
            models.CheckConstraint(
                check=models.Q(query_time__isnull=False),
                name="query_time_present" 
                )
        ]  
        
       
        
        permissions = [("can_view_all_searches", "Can view all searches")]
        
       
       
       
    def save(self, *args, **kwargs): 
        
         
        """Override save to enforce limits.""" 
        user = self.session.user

        # Enforce daily search limit
        today = timezone.now().date()
        daily_search_count = Search.objects.filter(
            session__user=user,
            query_time__date=today
        ).count()

        if daily_search_count >= 100:
            raise ValidationError("Daily search limit reached. Try again tomorrow.")

        # Enforce session query limit
        if self.session.query_count >= 20:
            raise ValueError("Session query limit reached. Start a new session.")

        # Increment counters
        self.session.add_query()
        super().save(*args, **kwargs)
    
    
   
    
    def __str__(self):
        return f"Search by {self.user.email} at {self.query_time}"

        
    def get_summary(self):
        """Returns a truncated version of the query text for display."""
        return self.query_text[:75] + "..." if len(self.query_text) > 75 else self.query_text

