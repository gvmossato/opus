from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User

#from .models import UserData
#from .forms import UserDataForm


class UserDetailView(generic.DetailView):
    model = User
    template_name = 'appsite/detail.html'
    context_object_name = 'user'
