from django.views import generic
from django.urls import reverse_lazy

from .models import UserData
from .forms import UserDataForm

class UserCreateView(generic.CreateView):
    form_class = UserDataForm
    template_name = 'appsite/index.html'
    context_object_name = 'user'

    def get_success_url(self):
        return reverse_lazy('appsite:detail', args=(self.object.id, ))

class UserDetailView(generic.DetailView):
    model = UserData
    template_name = 'appsite/detail.html'
    context_object_name = 'user'
