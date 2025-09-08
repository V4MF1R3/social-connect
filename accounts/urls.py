from django.urls import path
from .views import RegisterView, ProfileView, PasswordResetView, PasswordResetConfirmView, ChangePasswordView, VerifyEmailView, UserSearchView, UserProfileDetailView
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenBlacklistView, 
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('users/me/', ProfileView.as_view(), name='profile'),
    path('users/', UserSearchView.as_view(), name='user_search'),
    path('users/<int:user_id>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
