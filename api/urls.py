from django.urls import path
from .views import TaskList, TaskDetail

urlpatterns = [
    path('appsite/<int:pk>/', TaskDetail.as_view()),
    path('appsite/', TaskList.as_view()),
]
