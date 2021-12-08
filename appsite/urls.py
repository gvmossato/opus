from django.urls import path, include
from . import views

app_name='appsite'

urlpatterns = [
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('list_create/', views.ListCreateView.as_view(), name='list_create'),
    path('list/<int:pk>/', views.ListDetailView.as_view(), name='list_detail'),
    path('list_update/<int:pk>/', views.ListUpdateView.as_view(), name='list_update'),
    path('list/<int:pk>/invite/', views.InviteCreateView.as_view(), name='invite'),
    path('list/<int:pk>/jobs/', views.JobUpdateView.as_view(), name='job_update'),
    path('list/<int:pk>/invite_up/', views.invite_up, name='invite_up'),
    path('list/<int:pk>/invite_down/', views.invite_down, name='invite_down'),
]
