from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'full_name', 'is_premium', 'role')
    list_filter = ('is_premium', 'role', 'is_verified', 'preferred_language')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-username',)
