from .models import List, Job
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from appsite.forms import ListForm, InviteForm
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
        job = Job(active_invite=False, list_id=self.object.id, user_id=self.request.user.id, type=1)
        job.save()

        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class ListDetailView(generic.DetailView):
    model = List
    template_name = 'appsite/list_detail.html'
    context_object_name = 'list'
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs) # context padrão

        #Pegando os objetos de Job de acordo com o job_type (cargo)
        creator = Job.objects.filter(list_id=self.kwargs['pk'], type=1)
        admin = Job.objects.filter(list_id=self.kwargs['pk'], type=2)
        follower = Job.objects.filter(list_id=self.kwargs['pk'], type=3)
        guest = Job.objects.filter(list_id=self.kwargs['pk'], type=4)

        #Pegando somente os IDs de usuário de cada um deles
        creator_id = creator.values_list('user_id', flat=True)
        admin_id = admin.values_list('user_id', flat=True)
        follower_id = follower.values_list('user_id', flat=True)
        guest_id = guest.values_list('user_id', flat=True)

        #Pegando os objetos de User
        try:
            creator_user = User.objects.get(pk__in=creator_id)
        except:
            creator_user = None
        try:
            admin_user = User.objects.get(pk__in=admin_id)
        except:
            admin_user = None
        try:
            follower_user = User.objects.get(pk__in=follower_id)
        except:
            follower_user = None
        try:
            guest_user = User.objects.get(pk__in=guest_id)
        except:
            guest_user = None

        print(creator_id)

        #Montando os contextos
        context['creator_user'] = creator_user
        context['admin_user'] = admin_user
        context['follower_user'] = follower_user
        context['guest_user'] = guest_user

        return context


class ListUpdateView(generic.UpdateView):
    model = List
    form_class = ListForm
    template_name = 'appsite/list_update.html'

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, )) #redirecting to lists' page


class InviteCreateView(generic.CreateView):
    form_class = InviteForm
    template_name = 'appsite/invite.html'
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.list = List.objects.get(pk=self.kwargs['pk'])
        self.object.active_invite = True
        self.object.type = 4
        self.object.save()

        return super(InviteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('appsite:invite', args=(self.kwargs['pk'], )) #redirecting to invite page