from django.db import models
from django.utils import timezone
from authentication.models import CustomUser
from search.models import Search  


class Interaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="interactions")
    search = models.ForeignKey(Search, on_delete=models.CASCADE, related_name="interactions")
    rating = models.IntegerField(null=True, blank=True)  # Allows users to rate the response, e.g., 1-5 scale
    feedback = models.TextField(null=True, blank=True)  # Optional user feedback on the response
    interaction_type = models.CharField(max_length=20, choices=[("clarify", "Clarify"), ("rate", "Rate"), ("comment", "Comment")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction by {self.user.email} for search {self.search.id}"

    class Meta:
        ordering = ["-created_at"]
