#!/usr/bin/env python
"""
OAuth Setup Script
This script helps you set up the OAuth application properly.
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oauth.settings')
django.setup()

from django.core.management import execute_from_command_line
from oauth2_provider.models import Application
from django.contrib.auth.models import User

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("✅ Migrations completed!")

def create_superuser():
    """Create a superuser if one doesn't exist"""
    if not User.objects.filter(is_superuser=True).exists():
        print("👤 Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Superuser created! Username: admin, Password: admin123")
    else:
        print("👤 Superuser already exists!")

def create_oauth_application():
    """Create a default OAuth application"""
    app_name = "Default OAuth App"
    
    # Check if app already exists
    if Application.objects.filter(name=app_name).exists():
        app = Application.objects.get(name=app_name)
        print(f"📱 OAuth application '{app_name}' already exists!")
    else:
        print("📱 Creating OAuth application...")
        app = Application.objects.create(
            name=app_name,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            redirect_uris='http://localhost:8000/auth/complete/oauth2/',
        )
        print("✅ OAuth application created!")
    
    print(f"""
📋 OAuth Application Details:
   Name: {app.name}
   Client ID: {app.client_id}
   Client Secret: {app.client_secret}
   Redirect URI: http://localhost:8000/auth/complete/oauth2/
   
🔗 Authorization URL: http://localhost:8000/o/authorize/
🔗 Token URL: http://localhost:8000/o/token/
""")
    
    return app

def display_setup_instructions():
    """Display setup instructions for OAuth providers"""
    print("""
🛠️  OAuth Provider Setup Instructions:

1. GOOGLE OAUTH SETUP:
   - Go to: https://console.developers.google.com/
   - Create a new project or select existing one
   - Enable Google+ API and Google OAuth2 API
   - Go to Credentials → Create OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: http://localhost:8000/auth/complete/google-oauth2/
   - Copy Client ID and Client Secret to your .env file

2. GITHUB OAUTH SETUP:
   - Go to: https://github.com/settings/applications/new
   - Application name: Your App Name
   - Homepage URL: http://localhost:8000
   - Authorization callback URL: http://localhost:8000/auth/complete/github/
   - Copy Client ID and Client Secret to your .env file

3. FACEBOOK OAUTH SETUP:
   - Go to: https://developers.facebook.com/apps/
   - Create a new app
   - Add Facebook Login product
   - Valid OAuth Redirect URIs: http://localhost:8000/auth/complete/facebook/
   - Copy App ID and App Secret to your .env file

📝 Update your .env file with the actual OAuth credentials:
   GOOGLE_OAUTH2_KEY=your-actual-google-client-id
   GOOGLE_OAUTH2_SECRET=your-actual-google-client-secret
   GITHUB_KEY=your-actual-github-client-id
   GITHUB_SECRET=your-actual-github-client-secret
   FACEBOOK_KEY=your-actual-facebook-app-id
   FACEBOOK_SECRET=your-actual-facebook-app-secret
""")

def main():
    print("🚀 Starting OAuth Setup...")
    print("=" * 50)
    
    try:
        # Run migrations
        run_migrations()
        
        # Create superuser
        create_superuser()
        
        # Create OAuth application
        oauth_app = create_oauth_application()
        
        # Display instructions
        display_setup_instructions()
        
        print("=" * 50)
        print("✅ Setup completed successfully!")
        print("🌐 You can now run: python manage.py runserver")
        print("🔗 Visit: http://localhost:8000")
        print("⚙️  Admin panel: http://localhost:8000/admin")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
