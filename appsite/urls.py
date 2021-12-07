from django.urls import path, include
from . import views

app_name='appsite'

urlpatterns = [
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
]
