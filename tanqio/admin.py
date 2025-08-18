from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from oauth2_provider.models import Application, AccessToken, RefreshToken
from .models import UserProfile, OAuthApplication

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'provider_id', 'created_at']
    list_filter = ['provider', 'created_at']
    search_fields = ['user__username', 'user__email', 'provider_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OAuthApplication)
class OAuthApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_id', 'client_type', 'authorization_grant_type', 'is_active']
    list_filter = ['client_type', 'authorization_grant_type', 'is_active']
    search_fields = ['name', 'client_id']
    readonly_fields = ['client_id', 'client_secret']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'client_type', 'authorization_grant_type')
        }),
        ('URLs', {
            'fields': ('redirect_uris', 'website_url', 'logo_url')
        }),
        ('Credentials', {
            'fields': ('client_id', 'client_secret'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_active', 'skip_authorization')
        }),
    )

# Customize the default OAuth2 admin
class CustomApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_id', 'client_type', 'authorization_grant_type']
    list_filter = ['client_type', 'authorization_grant_type']
    search_fields = ['name', 'client_id']

class CustomAccessTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'user', 'application', 'scope', 'expires', 'created']
    list_filter = ['application', 'created', 'expires']
    search_fields = ['user__username', 'token']
    readonly_fields = ['token', 'created', 'updated']

class CustomRefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'user', 'application', 'created']
    list_filter = ['application', 'created']
    search_fields = ['user__username', 'token']
    readonly_fields = ['token', 'created', 'updated']

# Re-register User with profile inline
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Re-register OAuth2 models with custom admin
admin.site.unregister(Application)
admin.site.unregister(AccessToken)
admin.site.unregister(RefreshToken)

admin.site.register(Application, CustomApplicationAdmin)
admin.site.register(AccessToken, CustomAccessTokenAdmin)
admin.site.register(RefreshToken, CustomRefreshTokenAdmin)
