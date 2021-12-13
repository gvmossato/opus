from django.urls import path
from django.contrib.auth import views as auth_views

from .forms import CustomAuthForm
from .views import *

app_name='accounts'

urlpatterns = [
    path('', CreateUserView.as_view(), name='index'),
    path('redirect', login_redirect, name='redirect'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login')
]
