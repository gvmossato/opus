from django.urls import path, include
from . import views

app_name='accounts'

urlpatterns = [
    path('', views.CreateUserView.as_view(), name='index')
]
