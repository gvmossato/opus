from .models import List, Job, JobType
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from appsite.forms import ListForm
from django.shortcuts import get_object_or_404

#from .models import UserData
#from .forms import UserDataForm


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'appsite/detail.html'

    def get_context_data(self, **kwargs):
        # Envia qual usuário está logado e qual perfil foi acessado para o template
        current_user = self.request.user
        profile_user = User.objects.get(pk=self.kwargs['pk'])
          
        context = {
            'current_user' : current_user,
            'profile_user' : profile_user
        }

        return context


class ListCreateView(generic.CreateView):
    form_class = ListForm
    template_name = 'appsite/list_create.html'

    def get_success_url(self):
        # Vincula criador e lista no banco de dados
        job = Job(active_invite=False, list_id=self.object.id, user_id=self.request.user.id, type=JobType.objects.get(pk=1))
        job.save()

        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class ListDetailView(generic.DetailView):
    model = List
    template_name = 'appsite/list_detail.html'
    context_object_name = 'list'


class ListUpdateView(generic.UpdateView):
    model = List
    form_class = ListForm
    template_name = 'appsite/list_update.html'

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, )) #redirecting to lists' page
