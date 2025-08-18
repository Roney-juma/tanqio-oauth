from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from oauth2_provider.decorators import protected_resource
from oauth2_provider.models import Application, AccessToken, RefreshToken, Grant
from oauth2_provider.settings import oauth2_settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.utils import timezone
from .forms import CustomUserRegistrationForm, CustomAuthenticationForm, CustomPasswordResetForm
import json

def home(request):
    """Home page with login options"""
    context = {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'tanqio/home.html', context)

from django.utils.http import url_has_allowed_host_and_scheme

@csrf_exempt
def login_view(request):
    """Login page with OAuth options and email/password login"""
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('tanqio:home')

    if request.user.is_authenticated:
        if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({...})  # as you had
        return redirect(next_url)  # Redirect to next after login

    form = CustomAuthenticationForm()

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({...})  # as you had
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            # Ensure the next_url is safe
            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('tanqio:home')
        else:
            if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({...}, status=400)
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'tanqio/login.html', {'form': form, 'next': next_url})
def register_view(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('tanqio:profile')
    
    form = CustomUserRegistrationForm()
    
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully! Welcome, {user.get_full_name()}!')
            # Specify the backend explicitly when logging in after registration
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('tanqio:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return render(request, 'tanqio/register.html', {'form': form})

@login_required
def profile_view(request):
    """User profile page showing OAuth information"""
    social_auth = None
    provider_display = ""
    
    if hasattr(request.user, 'social_auth'):
        social_auth = request.user.social_auth.first()
        if social_auth:
            provider_map = {
                'google-oauth2': 'Google',
                'github': 'GitHub',
                'facebook': 'Facebook',
                'microsoft-graph': 'Microsoft',
                'azuread-oauth2': 'Azure AD'
            }
            provider_display = provider_map.get(social_auth.provider, social_auth.provider.title())
    
    context = {
        'user': request.user,
        'social_auth': social_auth,
        'provider_display': provider_display,
        'extra_data': social_auth.extra_data if social_auth else None,
    }
    return render(request, 'tanqio/profile.html', context)

@protected_resource(scopes=['read'])
def protected_api_view(request):
    """Protected API endpoint that requires OAuth token"""
    return JsonResponse({
        'message': 'Hello, authenticated user!',
        'user_id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'scopes': request.resource_owner.scope.split() if hasattr(request, 'resource_owner') else []
    })

@csrf_exempt
def api_user_info(request):
    """API endpoint to get user info with OAuth token"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    return JsonResponse({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'is_staff': request.user.is_staff,
        'date_joined': request.user.date_joined.isoformat(),
    })
@login_required
def oauth_applications_view(request):
    """View to display OAuth applications for the current user"""
    from oauth2_provider.models import Application
    
    if request.user.is_staff:
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(user=request.user)
    
    context = {
        'applications': applications,
    }
    return render(request, 'tanqio/oauth_apps.html', context)

def logout_view(request):
    """Custom logout view that handles OAuth provider logout"""
    social_auth = None
    provider_logout_url = None
    
    # Check if user has social auth
    if hasattr(request.user, 'social_auth'):
        social_auth = request.user.social_auth.first()
        
        if social_auth:
            provider = social_auth.provider
            
            # Generate logout URLs for different providers
            if provider == 'google-oauth2':
                provider_logout_url = 'https://accounts.google.com/logout'
            elif provider == 'github':
                provider_logout_url = 'https://github.com/logout'
            elif provider == 'microsoft-graph':
                provider_logout_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/logout'
            elif provider == 'azuread-oauth2':
                provider_logout_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/logout'
    
    # Clear Django session
    logout(request)

    # Add success message
    messages.success(request, 'You have been successfully logged out.')

    # If we have a provider logout URL, show confirm page with external link
    if provider_logout_url:
        return render(request, 'tanqio/logout_confirm.html', {
            'provider_logout_url': provider_logout_url,
            'provider': social_auth.provider if social_auth else None
        })

    # Otherwise redirect to home
    return redirect('tanqio:home')

def complete_logout_view(request):
    """Complete logout after provider logout"""
    messages.success(request, 'You have been completely logged out from all services.')
    return redirect('tanqio:home')

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    template_name = 'tanqio/password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('tanqio:password_reset_done')
    email_template_name = 'tanqio/password_reset_email.html'
    subject_template_name = 'tanqio/password_reset_subject.txt'

    def form_valid(self, form):
        messages.success(self.request, 'Password reset email has been sent!')
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view"""
    template_name = 'tanqio/password_reset_confirm.html'
    success_url = reverse_lazy('tanqio:password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully!')
        return super().form_valid(form)

from oauth2_provider.models import AccessToken

@csrf_exempt
@protected_resource(scopes=['read'])
def api_profile(request):
    try:
        user = request.user

        # Get Access Token object
        access_token_value = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]  # Extract Bearer token
        access_token = AccessToken.objects.get(token=access_token_value)

        # Get social auth information
        social_auth = None
        if hasattr(user, 'social_auth'):
            social_auth = user.social_auth.first()

        profile_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'social_auth': {
                'provider': social_auth.provider if social_auth else None,
                'uid': social_auth.uid if social_auth else None,
                'extra_data': social_auth.extra_data if social_auth else None,
            } if social_auth else None,
            'oauth_info': {
                'scopes': access_token.scope.split(),
                'application': access_token.application.name if access_token.application else None,
            }
        }

        return JsonResponse(profile_data)

    except Exception as e:
        print(f"Error in api_profile: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_auth_status(request):
    """API endpoint to check authentication status"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user_id': request.user.id,
            'username': request.user.username,
            'full_name': request.user.get_full_name(),
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'message': 'User is not authenticated'
        })

@csrf_exempt
@protected_resource(scopes=['write'])
def api_update_profile(request):
    """API endpoint to update user profile with OAuth token"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            # Check if email is already taken
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return JsonResponse({'error': 'Email already in use'}, status=400)
            user.email = data['email']
        
        user.save()
        
        return JsonResponse({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@protected_resource(scopes=['read'])
def api_oauth_applications(request):
    """API endpoint to list OAuth applications for the authenticated user"""
    user = request.user
    
    if user.is_staff:
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(user=user)
    
    apps_data = []
    for app in applications:
        apps_data.append({
            'id': app.id,
            'name': app.name,
            'client_id': app.client_id,
            'client_type': app.get_client_type_display(),
            'authorization_grant_type': app.get_authorization_grant_type_display(),
            'created': app.created.isoformat(),
            'updated': app.updated.isoformat(),
        })
    
    return JsonResponse({
        'applications': apps_data,
        'count': len(apps_data)
    })

@csrf_exempt
def api_health_check(request):
    """API endpoint for health check"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'OAuth Titan API',
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    })


from oauth2_provider.models import AccessToken, RefreshToken

@csrf_exempt
@protected_resource(scopes=['read', 'write'])
def api_logout(request):
    """
    API endpoint to revoke the user's access and refresh tokens (logout).
    """
    try:
        # Prefer revoking all tokens for the authenticated user to ensure complete logout
        if request.user.is_authenticated:
            AccessToken.objects.filter(user=request.user).delete()
            RefreshToken.objects.filter(user=request.user).delete()
            Grant.objects.filter(user=request.user).delete()

        # Additionally, if a specific bearer token is provided, ensure it is removed
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_value = auth_header.split(' ')[1] if ' ' in auth_header else None
        if token_value:
            AccessToken.objects.filter(token=token_value).delete()
            RefreshToken.objects.filter(access_token__token=token_value).delete()

    # Optional: remote revocation (RFC 7009) when accepting external tokens via introspection
        # If configured, attempt to revoke the access token and any refresh token provided in body
        from django.conf import settings
        revocation_url = getattr(settings, 'RESOURCE_SERVER_REVOCATION_URL', None)
        client_id = getattr(settings, 'RESOURCE_SERVER_CLIENT_ID', None)
        client_secret = getattr(settings, 'RESOURCE_SERVER_CLIENT_SECRET', None)
        if revocation_url and client_id and client_secret:
            import requests
            # Revoke access token
            if token_value:
                try:
                    requests.post(
                        revocation_url,
                        data={'token': token_value, 'token_type_hint': 'access_token'},
                        auth=(client_id, client_secret),
                        timeout=5,
                    )
                except Exception:
                    pass
            # Revoke refresh token if supplied in JSON body
            try:
                body = json.loads(request.body or '{}')
                refresh_token_value = body.get('refresh_token')
                if refresh_token_value:
                    try:
                        requests.post(
                            revocation_url,
                            data={'token': refresh_token_value, 'token_type_hint': 'refresh_token'},
                            auth=(client_id, client_secret),
                            timeout=5,
                        )
                    except Exception:
                        pass
            except Exception:
                pass

        # Add token to a local blacklist cache so any lag at issuer won't allow reuse
        try:
            if token_value:
                from django.core.cache import cache
                import hashlib
                token_hash = hashlib.sha256(token_value.encode('utf-8')).hexdigest()
                cache.set(f"exttoken:blacklist:{token_hash}", True, timeout=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        except Exception:
            pass

        return JsonResponse({'message': 'Successfully logged out from OAuth2 server'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# --- API endpoint to refresh access token using refresh token ---
from django.views.decorators.http import require_POST
from oauth2_provider.settings import oauth2_settings
import secrets

@csrf_exempt
@require_POST
def api_refresh_token(request):
    """
    API endpoint to exchange a refresh token for a new access token.
    """
    try:
        data = json.loads(request.body)
        refresh_token_value = data.get('refresh_token')
        client_id = data.get('client_id')

        if not refresh_token_value or not client_id:
            return JsonResponse({'error': 'Missing refresh_token or client_id'}, status=400)

        # Validate refresh token and client
        refresh_token = RefreshToken.objects.select_related('access_token', 'application', 'user').filter(token=refresh_token_value).first()
        if not refresh_token or not refresh_token.application or refresh_token.application.client_id != client_id:
            return JsonResponse({'error': 'Invalid refresh token or client'}, status=400)

        # Create new access token
        expires = timezone.now() + timezone.timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        new_token = secrets.token_urlsafe(30)
        access_token = AccessToken.objects.create(
            user=refresh_token.user,
            scope=refresh_token.access_token.scope,
            expires=expires,
            token=new_token,
            application=refresh_token.application
        )

        # Optionally, revoke the old access token
        refresh_token.access_token.delete()
        refresh_token.access_token = access_token
        refresh_token.save()

        return JsonResponse({
            'access_token': access_token.token,
            'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            'token_type': 'Bearer',
            'scope': access_token.scope,
            'refresh_token': refresh_token.token
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
