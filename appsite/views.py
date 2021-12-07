from .models import List, Job
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from appsite.forms import ListForm

#from .models import UserData
#from .forms import UserDataForm


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'appsite/detail.html'
    context_object_name = 'user'

class ListCreateView(generic.CreateView):
    form_class = ListForm
    template_name = 'appsite/list_create.html'

    def get_success_url(self):
        # registering recently created list to the user that created it 
        job = Job(active_invite = 0, list_id = self.object.id, user_id = self.request.user.id)
        job.save()
        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))

class ListDetailView(generic.DetailView):
    model = List
    template_name = 'appsite/list_detail.html'
    context_object_name = 'list'
