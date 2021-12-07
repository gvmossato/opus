from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserCreateView.as_view(), name='index'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='detail'),
]
