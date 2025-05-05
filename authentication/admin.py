from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'is_premium', 'role')
    list_filter = ('is_premium', 'role', 'is_verified', 'preferred_language')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-username',)



# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import UserRating

@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'star_rating', 'feedback_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'feedback')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        """Display user's email in the list view"""
        return obj.user.email
    user_email.short_description = 'User'
    
    def star_rating(self, obj):
        """Display stars instead of numbers for rating"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = ''
        if obj.rating >= 4:
            color = 'green'
        elif obj.rating >= 3:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{}</span>', color, stars)
    star_rating.short_description = 'Rating'
    
    def feedback_preview(self, obj):
        """Display a preview of feedback text"""
        if not obj.feedback:
            return '-'
        preview = obj.feedback[:50]
        if len(obj.feedback) > 50:
            preview += '...'
        return preview
    feedback_preview.short_description = 'Feedback'
    
    # Advanced option - add a custom filter to see ratings within date ranges
    class RatingPeriodListFilter(admin.SimpleListFilter):
        title = 'rating period'
        parameter_name = 'period'
        
        def lookups(self, request, model_admin):
            return (
                ('recent', 'Last 30 days'),
                ('quarter', 'Last quarter'),
                ('biannual', 'Last 6 months'),
                ('annual', 'Last year'),
            )
        
        def queryset(self, request, queryset):
            from django.utils import timezone
            from datetime import timedelta
            
            if self.value() == 'recent':
                return queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))
            if self.value() == 'quarter':
                return queryset.filter(created_at__gte=timezone.now() - timedelta(days=90))
            if self.value() == 'biannual':
                return queryset.filter(created_at__gte=timezone.now() - timedelta(days=182))
            if self.value() == 'annual':
                return queryset.filter(created_at__gte=timezone.now() - timedelta(days=365))
            return queryset
    
    list_filter = ('rating', 'created_at', RatingPeriodListFilter)