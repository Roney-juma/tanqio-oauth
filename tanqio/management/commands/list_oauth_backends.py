from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse

class Command(BaseCommand):
    help = 'List all available OAuth backends and their URLs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Available OAuth Backends ===\n'))
        
        backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        
        # Extract social auth backends
        social_backends = [b for b in backends if 'social_core.backends' in b]
        
        backend_info = {
            'social_core.backends.google.GoogleOAuth2': {
                'name': 'google-oauth2',
                'display': 'Google OAuth 2.0',
                'test_url': '/auth/login/google-oauth2/'
            },
            'social_core.backends.github.GithubOAuth2': {
                'name': 'github',
                'display': 'GitHub OAuth',
                'test_url': '/auth/login/github/'
            },
            'social_core.backends.facebook.FacebookOAuth2': {
                'name': 'facebook',
                'display': 'Facebook OAuth',
                'test_url': '/auth/login/facebook/'
            },
            'social_core.backends.microsoft.MicrosoftOAuth2': {
                'name': 'microsoft-graph',
                'display': 'Microsoft Graph OAuth',
                'test_url': '/auth/login/microsoft-graph/'
            },
            'social_core.backends.azuread.AzureADOAuth2': {
                'name': 'azuread-oauth2',
                'display': 'Azure AD OAuth 2.0',
                'test_url': '/auth/login/azuread-oauth2/'
            },
        }
        
        for backend in social_backends:
            if backend in backend_info:
                info = backend_info[backend]
                self.stdout.write(f"✓ {info['display']}")
                self.stdout.write(f"  Backend: {backend}")
                self.stdout.write(f"  URL Name: {info['name']}")
                self.stdout.write(f"  Test URL: {info['test_url']}")
                self.stdout.write("")
        
        self.stdout.write("=== Test URLs ===")
        self.stdout.write("You can test these URLs in your browser:")
        for backend in social_backends:
            if backend in backend_info:
                info = backend_info[backend]
                self.stdout.write(f"http://localhost:8000{info['test_url']}")
        
        self.stdout.write(f"\n=== Redirect URIs for Provider Configuration ===")
        self.stdout.write("Configure these in your OAuth provider:")
        for backend in social_backends:
            if backend in backend_info:
                info = backend_info[backend]
                self.stdout.write(f"• {info['display']}: http://localhost:8000/auth/complete/{info['name']}/")
                
        self.stdout.write(self.style.SUCCESS(f'\n✓ Found {len(social_backends)} OAuth backends configured!'))
