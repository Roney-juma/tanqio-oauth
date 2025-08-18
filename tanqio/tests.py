from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken, RefreshToken, Grant


class LogoutRevocationTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='alice', password='password', email='alice@example.com')
		self.client = Client()
		self.client.force_login(self.user)

		# Create an OAuth application
		self.app = Application.objects.create(
			name='Test App',
			user=self.user,
			client_type=Application.CLIENT_CONFIDENTIAL,
			authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
		)

		# Create tokens and a grant for this user
		self.access_token = AccessToken.objects.create(
			user=self.user,
			scope='read write',
			expires=timezone.now() + timezone.timedelta(hours=1),
			token='access123',
			application=self.app,
		)
		self.refresh_token = RefreshToken.objects.create(
			user=self.user,
			token='refresh123',
			application=self.app,
			access_token=self.access_token,
		)
		self.grant = Grant.objects.create(
			user=self.user,
			code='code123',
			application=self.app,
			expires=timezone.now() + timezone.timedelta(minutes=10),
			redirect_uri='http://localhost/callback',
			scope='read write',
		)

	def test_logout_revoke_all_tokens(self):
		# Ensure records exist before logout
		self.assertTrue(AccessToken.objects.filter(user=self.user).exists())
		self.assertTrue(RefreshToken.objects.filter(user=self.user).exists())
		self.assertTrue(Grant.objects.filter(user=self.user).exists())

		# Hit the logout view
		resp = self.client.get(reverse('tanqio:logout'))
		self.assertIn(resp.status_code, (200, 302))

		# All tokens and grants for this user should be gone
		self.assertFalse(AccessToken.objects.filter(user=self.user).exists())
		self.assertFalse(RefreshToken.objects.filter(user=self.user).exists())
		self.assertFalse(Grant.objects.filter(user=self.user).exists())

