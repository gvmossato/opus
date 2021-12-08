from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from .models import List, Job
from .forms import ListForm, InviteForm, JobForm

# ====== #
# CREATE #
# ====== #

class ListCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = ListForm
    template_name = 'appsite/list_create.html'

    def get_success_url(self):
        # Vincula criador e lista no banco de dados
        job = Job(active_invite=False, list_id=self.object.id, user_id=self.request.user.id, type=4)
        job.save()

        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class InviteCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = InviteForm
    template_name = 'appsite/invite.html'
    
    # Define campos padrão do formulário
    def form_valid(self, form):
        self.object = form.save(commit=False) # Retém dados enviados pelo usuário
        self.object.list = List.objects.get(pk=self.kwargs['pk'])
        self.object.active_invite = True
        self.object.type = 1
        self.object.save()

        return super(InviteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('appsite:invite', args=(self.kwargs['pk'], )) #redirecting to invite page

# ==== #
# READ #
# ==== #

class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'appsite/detail.html'

    # Envia para o template qual usuário está logado e qual perfil foi acessado
    def get_context_data(self, **kwargs):        
        current_user = self.request.user
        profile_user = User.objects.get(pk=self.kwargs['pk'])
          
        context = {
            'current_user' : current_user,
            'profile_user' : profile_user
        }

        return context


class ListDetailView(LoginRequiredMixin, generic.DetailView):
    model = List
    template_name = 'appsite/list_detail.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)           # Obtém context padrão
        keys = [None, 'guest', 'follower', 'admin', 'creator'] # Mapeia um número para cada cargo

        for job_type in range(1, 5):            
            user_job = Job.objects.filter(list_id=self.kwargs['pk'], type=job_type) # Obtém usuários com um cargo específico
            user_id = user_job.values_list('user_id', flat=True)                    # Utiliza o cargo para obter o id do usuári
            try:
                user = User.objects.filter(pk__in=user_id) # Obtém o objeto usuário atavés do id
            except:                
                user = None # Caso não existam usuários com o cargo da iteração

            context[keys[job_type]] = user # Atualiza context

        return context

# ====== #
# UPDATE #
# ====== #

class ListUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = List
    form_class = ListForm
    template_name = 'appsite/list_update.html'

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, )) # Redireciona para a página da lista

class JobUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'appsite/job_update.html'

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, )) # Redireciona para a página da lista

# ====== #
# CUSTOM #
# ====== #

def invite_up(request, pk):
    job = Job.objects.get(pk=pk)
    job.active_invite = False #accepting request
    job.type = 2
    job.save()
    
    return HttpResponseRedirect(
        reverse('appsite:detail', args=(job.user_id, )))