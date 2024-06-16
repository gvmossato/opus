from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import CustomAuthForm
from .views import *

app_name='accounts'

urlpatterns = [
    # Sign up & Sign in
    path('', signup, name='index'),
    path('redirect', login_redirect, name='redirect'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login'),

    # Password reset
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # Profile
    path('user/<int:pk>/', UserDetailView.as_view(), name='profile_detail'),
    path('user/<int:pk>/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('user/<int:pk>/invite/',      InviteUpdateView.as_view(),    name='invite_update'),
    path('user/<int:pk>/invite/all/',  InviteUpdateAllView.as_view(), name='invite_update_all'),
]
