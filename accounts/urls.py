from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from .forms import CustomAuthForm
from .views import *

app_name='accounts'

urlpatterns = [
    # Sign up/Sign in
    path('', views.signup, name='index'),
    path('redirect', login_redirect, name='redirect'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

    # Password reset
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html',
         success_url = reverse_lazy('accounts:password_reset_complete')), name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]

