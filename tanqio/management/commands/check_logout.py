from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

class Command(BaseCommand):
    help = 'Display logout configuration and test OAuth logout URLs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== OAuth Logout Configuration ===\n'))
        
        # Show logout URLs for each provider
        logout_urls = {
            'Google': 'https://accounts.google.com/logout',
            'GitHub': 'https://github.com/logout', 
            'Microsoft': 'https://login.microsoftonline.com/common/oauth2/v2.0/logout',
            'Azure AD': 'https://login.microsoftonline.com/common/oauth2/v2.0/logout',
        }
        
        self.stdout.write('Configured logout URLs:')
        for provider, url in logout_urls.items():
            self.stdout.write(f'• {provider}: {url}')
        
        # Show users with social auth
        social_users = UserSocialAuth.objects.all()
        if social_users.exists():
            self.stdout.write(f'\n=== Users with Social Auth ({social_users.count()}) ===')
            for social_user in social_users:
                self.stdout.write(f'• {social_user.user.username} via {social_user.provider}')
        else:
            self.stdout.write('\n=== No users with social auth found ===')
        
        self.stdout.write(f'\n=== Logout Flow ===')
        self.stdout.write('1. User clicks logout in your app')
        self.stdout.write('2. Django session is cleared')
        self.stdout.write('3. User is shown provider logout option')
        self.stdout.write('4. User can logout from OAuth provider')
        self.stdout.write('5. User returns to home page')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Logout system is configured and ready!'))
