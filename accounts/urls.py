from django.urls import path, include
from django.conf.urls import url

from . import views
from .views import *

app_name='accounts'

urlpatterns = [
    path('', views.CreateUserView.as_view(), name='index'),
    path('redirect', login_redirect, name='redirect'),
]
