from django.urls import path
from .views import ListTask

urlpatterns = [
    path('appsite/', ListTask.as_view()),
]