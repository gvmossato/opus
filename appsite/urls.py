from django.urls import path, include
from . import views

app_name='appsite'

urlpatterns = [
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('user/<int:pk>/invite', views.InviteUpdateView.as_view(), name='invite_update'),
    path('user/<int:pk>/invite_all', views.InviteUpdateAllView.as_view(), name='invite_update_all'),
    path('user/<int:pk>/update', views.ProfileUpdateView.as_view(), name='profile_update'),

    path('list_create/<int:pk>',          views.ListCreateView.as_view(), name='list_create'),    
    path('list_update/<int:pk>/', views.ListUpdateView.as_view(), name='list_update'),
    path('list/<int:pk>/untrack/', views.ListUntrackView.as_view(), name='list_untrack'),

    path('list/<int:pk>/',        views.ListDetailView.as_view(),   name='list_detail'),
    path('list/<int:pk>/invite/', views.InviteCreateView.as_view(), name='invite'),
    path('list/<int:pk>/jobs/',   views.JobUpdateView.as_view(),    name='job_update'),
    path('list/<int:pk>/tag/',    views.TagCreateView.as_view(),    name='tag_create'),
    path('list/<int:pk>/follow/', views.TagFollowView.as_view(),    name='tag_follow'),
    path('list/<int:pk>/delete/', views.ListDeleteView.as_view(),   name='list_delete'),
    path('list/<int:pk>/tag_unfollow', views.TagUnfollowView.as_view(), name='tag_unfollow' ),
    
    path('list/tag_add/<int:pk>/',                   views.TagAddView.as_view(),    name='tag_add'),
    path('list/task_create/<int:list_id>/',          views.task_create,             name='task_create'),
    path('list/task_update/<int:pk>/',               views.TaskUpdateView.as_view(),name = 'task_update'),
    path('list/task_delete/<int:pk>/<int:list_id>/', views.TaskDeleteView.as_view(),name = 'task_delete'),
]
