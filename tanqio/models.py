from django.db import models
from django.contrib.auth.models import User
from oauth2_provider.models import AbstractAccessToken, AbstractApplication

class UserProfile(models.Model):
    """Extended user profile for additional OAuth data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)
    provider = models.CharField(max_length=50, blank=True)
    provider_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class OAuthApplication(AbstractApplication):
    """Custom OAuth Application model with additional fields"""
    description = models.TextField(blank=True)
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'oauth_applications'
