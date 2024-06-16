from rest_framework import generics

from appsite.models import Task

from .serializers import TaskSerializer


class ListTask(generics.ListAPIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
