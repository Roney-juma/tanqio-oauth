from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from oauth2_provider.oauth2_validators import OAuth2Validator
import hashlib
import requests


class CustomOAuth2Validator(OAuth2Validator):
    """
    Validates local Django OAuth Toolkit (DOT) tokens first; if not valid, performs
    RFC 7662 token introspection against an external resource server so that
    endpoints protected by DOT can also accept that server's access tokens.

    Settings used (add to settings.py):
      - RESOURCE_SERVER_INTROSPECTION_URL
      - RESOURCE_SERVER_CLIENT_ID
      - RESOURCE_SERVER_CLIENT_SECRET
      - OAUTH_INTROSPECTION_ALLOWED_CLIENT_IDS (optional allowlist)
    """

    def validate_bearer_token(self, token, scopes, request):
        # 1) Try normal local validation via DOT
        if super().validate_bearer_token(token, scopes, request):
            return True

        # 2) Block tokens that have been explicitly blacklisted (e.g., via logout)
        try:
            token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
            if cache.get(f"exttoken:blacklist:{token_hash}"):
                return False
        except Exception:
            pass

        # 3) Fallback to remote introspection
        introspection_url = getattr(settings, 'RESOURCE_SERVER_INTROSPECTION_URL', None)
        client_id = getattr(settings, 'RESOURCE_SERVER_CLIENT_ID', None)
        client_secret = getattr(settings, 'RESOURCE_SERVER_CLIENT_SECRET', None)
        allowed_client_ids = getattr(settings, 'OAUTH_INTROSPECTION_ALLOWED_CLIENT_IDS', []) or []

        if not introspection_url or not client_id or not client_secret:
            return False

        try:
            resp = requests.post(
                introspection_url,
                data={'token': token},
                auth=(client_id, client_secret),
                timeout=5,
            )
        except Exception:
            return False

        if resp.status_code != 200:
            return False

        try:
            data = resp.json()
        except ValueError:
            return False

        if not data.get('active'):
            return False

        # Optional: ensure the token belongs to an allowed client/application
        token_client_id = str(data.get('client_id') or data.get('clientid') or '')
        if allowed_client_ids and token_client_id not in allowed_client_ids:
            return False

        # Scope check
        raw_scopes = data.get('scope') or []
        token_scopes = raw_scopes.split() if isinstance(raw_scopes, str) else list(raw_scopes)
        if scopes:
            if any(s not in token_scopes for s in scopes):
                return False

        request.scopes = token_scopes

        # Best-effort user resolution
        User = get_user_model()
        user = None
        uid = data.get('sub') or data.get('user_id') or data.get('uid')
        email = data.get('email')
        username = data.get('username')
        for field, value in (('id', uid), ('email', email), ('username', username)):
            if not value:
                continue
            try:
                user = User.objects.get(**{field: value})
                break
            except User.DoesNotExist:
                continue

        request.user = user or AnonymousUser()
        request.client = None
        request.access_token = None
        request.extra_credentials = data
        return True
