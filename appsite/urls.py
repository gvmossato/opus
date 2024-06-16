from django.urls import path

from . import views

app_name='appsite'

urlpatterns = [
    ### Profile ###


    path('user/<int:pk>/list/create/', views.ListCreateView.as_view(),      name='list_create'),

    ### List ###
    path('list/<int:pk>/',              views.ListDetailView.as_view(),   name='list_detail'),
    path('list/<int:pk>/update/',       views.ListUpdateView.as_view(),   name='list_update'),
    path('list/<int:pk>/delete/',       views.ListDeleteView.as_view(),   name='list_delete'),
    path('list/<int:pk>/menu/',         views.ListMenuTemplate.as_view(), name='list_menu'),
    path('list/<int:pk>/untrack/',      views.ListUntrackView.as_view(),  name='list_untrack'),
    path('list/<int:pk>/jobs/',         views.JobUpdateView.as_view(),    name='job_update'),
    path('list/<int:pk>/task/create/',  views.TaskCreateView.as_view(),   name='task_create'),
    path('list/<int:pk>/tag/create/',   views.TagCreateView.as_view(),    name='tag_create'),
    path('list/<int:pk>/tag/follow/',   views.TagFollowView.as_view(),    name='tag_follow'),
    path('list/<int:pk>/tag/unfollow/', views.TagUnfollowView.as_view(),  name='tag_unfollow'),

    ### Task ###
    path('task/<int:pk>/update/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),

    ### Tag ###
    path('tag/<int:pk>/add/', views.TagAddView.as_view(), name='tag_add'),
]
