from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import List, Job
from .forms import ListForm, InviteForm

# ====== #
# CREATE #
# ====== #

class ListCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = ListForm
    template_name = 'appsite/list_create.html'

    def get_success_url(self):
        # Vincula criador e lista no banco de dados
        job = Job(active_invite=False, list_id=self.object.id, user_id=self.request.user.id, type=0)
        job.save()

        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class InviteCreateView(generic.CreateView):
    form_class = InviteForm
    template_name = 'appsite/invite.html'
    
    # Define campos padrão do formulário
    def form_valid(self, form):
        self.object = form.save(commit=False) # Retém dados enviados pelo usuário
        self.object.list = List.objects.get(pk=self.kwargs['pk'])
        self.object.active_invite = True
        self.object.type = 3
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
        context = super().get_context_data(**kwargs)     # Obtém context padrão
        keys = ['creator', 'admin', 'follower', 'guest'] # Mapeia um número para cada cargo

        for type in range(0, 4):            
            user_job = Job.objects.filter(list_id=self.kwargs['pk'], type=type) # Obtém usuários com um cargo específico
            user_id = user_job.values_list('user_id', flat=True)                # Utiliza o cargo para obter o id do usuário
            try:
                user = User.objects.get(pk__in=user_id) # Obtém o objeto usuário atavés do id
            except:
                user = None # Caso não existam usuários com o cargo da iteração

            context[keys[type]] = user # Atualiza context

        return context

# ====== #
# UPDATE #
# ====== #

class ListUpdateView(generic.UpdateView):
    model = List
    form_class = ListForm
    template_name = 'appsite/list_update.html'

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, )) #redirecting to lists' page
