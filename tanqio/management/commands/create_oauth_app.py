from django.core.management.base import BaseCommand
from oauth2_provider.models import Application
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create OAuth2 application for testing'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, default='Test App', help='Application name')
        parser.add_argument('--client-type', type=str, default='confidential', 
                           choices=['confidential', 'public'], help='Client type')
        parser.add_argument('--grant-type', type=str, default='authorization-code',
                           choices=['authorization-code', 'client-credentials'], 
                           help='Authorization grant type')

    def handle(self, *args, **options):
        app_name = options['name']
        client_type = Application.CLIENT_CONFIDENTIAL if options['client_type'] == 'confidential' else Application.CLIENT_PUBLIC
        grant_type = Application.GRANT_AUTHORIZATION_CODE if options['grant_type'] == 'authorization-code' else Application.GRANT_CLIENT_CREDENTIALS

        application = Application.objects.create(
            name=app_name,
            client_type=client_type,
            authorization_grant_type=grant_type,
            redirect_uris='http://localhost:8000/auth/complete/oauth/',
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created OAuth2 application:\n'
                f'Name: {application.name}\n'
                f'Client ID: {application.client_id}\n'
                f'Client Secret: {application.client_secret}\n'
                f'Client Type: {application.get_client_type_display()}\n'
                f'Grant Type: {application.get_authorization_grant_type_display()}'
            )
        )
