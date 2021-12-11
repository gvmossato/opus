from django.urls import path, include
from . import views

app_name='appsite'

urlpatterns = [
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('user/<int:pk>/invite', views.InviteUpdateView.as_view(), name='invite_update'),
    path('user/<int:pk>/update', views.ProfileUpdateView.as_view(), name='profile_update'),

    path('list_create/',          views.ListCreateView.as_view(), name='list_create'),    
    path('list_update/<int:pk>/', views.ListUpdateView.as_view(), name='list_update'),

    path('list/<int:pk>/',        views.ListDetailView.as_view(),   name='list_detail'),
    path('list/<int:pk>/invite/', views.InviteCreateView.as_view(), name='invite'),
    path('list/<int:pk>/jobs/',   views.JobUpdateView.as_view(),    name='job_update'),
    path('list/<int:pk>/tag/',    views.TagCreateView.as_view(),    name='tag_create'),
    path('list/<int:pk>/follow/', views.TagFollowView.as_view(),    name='tag_follow'),
    
    path('list/tag_add/<int:task_id>/<int:tag_id>/', views.tag_add,     name='tag_add'),
    path('list/task_create/<int:list_id>/',          views.task_create, name='task_create'),
    path('list/task_update/<int:pk>/', views.TaskUpdateView.as_view(), name = 'task_update')
]
