from django.urls import path, include
from . import views

app_name='appsite'

urlpatterns = [
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('list_create/', views.ListCreateView.as_view(), name='list_create'),
    path('list/<int:pk>/', views.ListDetailView.as_view(), name='list_detail'),
    path('list_update/<int:pk>/', views.ListUpdateView.as_view(), name='list_update')
]
