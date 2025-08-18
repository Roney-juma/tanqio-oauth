from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Display Microsoft OAuth configuration status and setup instructions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Microsoft OAuth Configuration Status ===\n'))
        
        # Check Microsoft Graph settings
        microsoft_key = getattr(settings, 'SOCIAL_AUTH_MICROSOFT_GRAPH_KEY', '')
        microsoft_secret = getattr(settings, 'SOCIAL_AUTH_MICROSOFT_GRAPH_SECRET', '')
        
        self.stdout.write(f"Microsoft Graph Client ID: {'✓ Configured' if microsoft_key and microsoft_key != 'your-microsoft-client-id' else '✗ Not configured'}")
        self.stdout.write(f"Microsoft Graph Secret: {'✓ Configured' if microsoft_secret and microsoft_secret != 'your-microsoft-client-secret' else '✗ Not configured'}")
        
        # Check Azure AD settings
        azure_key = getattr(settings, 'SOCIAL_AUTH_AZUREAD_OAUTH2_KEY', '')
        azure_secret = getattr(settings, 'SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET', '')
        azure_tenant = getattr(settings, 'SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID', '')
        
        self.stdout.write(f"Azure AD Client ID: {'✓ Configured' if azure_key and azure_key != 'your-azure-client-id' else '✗ Not configured'}")
        self.stdout.write(f"Azure AD Secret: {'✓ Configured' if azure_secret and azure_secret != 'your-azure-client-secret' else '✗ Not configured'}")
        self.stdout.write(f"Azure AD Tenant: {'✓ Configured' if azure_tenant and azure_tenant != 'common' else '✓ Using common tenant'}")
        
        self.stdout.write('\n=== Required Redirect URIs ===')
        self.stdout.write('Configure these redirect URIs in your Azure app registration:')
        self.stdout.write('• http://localhost:8000/auth/complete/microsoft-graph/')
        self.stdout.write('• http://localhost:8000/auth/complete/azuread-oauth2/')
        
        self.stdout.write('\n=== Setup Instructions ===')
        self.stdout.write('1. Go to https://portal.azure.com/')
        self.stdout.write('2. Navigate to Azure Active Directory > App registrations')
        self.stdout.write('3. Create a new registration or use existing one')
        self.stdout.write('4. Configure redirect URIs as shown above')
        self.stdout.write('5. Generate client secret in "Certificates & secrets"')
        self.stdout.write('6. Update your .env file with the credentials')
        
        if not (microsoft_key and microsoft_key != 'your-microsoft-client-id'):
            self.stdout.write(self.style.WARNING('\n⚠️  Microsoft OAuth is not properly configured. Please update your .env file.'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Microsoft OAuth appears to be configured!'))
