from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'tanqio'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/complete/', views.complete_logout_view, name='complete_logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile', views.profile_view),  # allow no trailing slash
    
    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tanqio/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tanqio/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # API URLs
    path('api/protected/', views.protected_api_view, name='protected_api'),
    path('api/user/', views.api_user_info, name='api_user_info'),
    path('api/profile/', views.api_profile, name='api_profile'),
    path('api/profile', views.api_profile),  # allow no trailing slash
    path('api/health/', views.api_health_check, name='api_health'),
    path('api/logout/', views.api_logout, name='api_logout'),
    # OAuth applications list
    path('oauth/apps/', views.oauth_applications_view, name='oauth_apps'),
    # Keep minimal APIs that exist in current views
]
