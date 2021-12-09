from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .models import List, Job, Tag, Follow, Task
from .forms import ListForm, InviteForm, JobForm, TagForm

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

#class FollowDetailView(LoginRequiredMixin, generic.DetailView):
    #model = List
    #template_name = 'appsite/follow_detail.html'
    #context_object_name = 'list'

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


def follow_tag(request, tag_id, source_id, list_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    list = get_object_or_404(List, pk=list_id)

    # getting all tasks that have the tag and come from the followed list
    tasks = tag.task.filter(list_id=source_id)
    # adding each of these tags to the user's list
    for task in tasks:
        # checking if the task is original in the list of destination
        task_filter = list.task_set.filter(original_id=task.original_id)
        if (task_filter):
            pass # not adding tasks that share the same original_id
        else:
            # adding the task to the list
            task2 = Task.objects.create(list_id=list_id, original_id = task.original_id, name = task.name, done = task.done)
            task2.save()
            # linking the tag to this newly created task
            tag.task.add(task2)
    
    # creating new follow object of following list, tag being followed and followed list id
    follow = Follow(list=List.objects.get(pk=list_id),tag=Tag.objects.get(pk=tag_id),source_id=source_id)
    follow.save()
    
    # updating user's permission to follower and removing list invite
    job = Job.objects.get(list_id=source_id, user_id=request.user.id)
    job.active_invite = False
    job.type = 2
    job.save()

    # redirecting to user's page
    return HttpResponseRedirect(reverse_lazy('appsite:detail', args=(request.user.id, )))


# ====== #
# CUSTOM #
# ====== #

def invite_up(request, pk):
    # list that will be followed
    list = List.objects.get(pk=pk)

    # creating list to store tags
    tags = []
    
    # creating loop to store tags of the followed list
    for task in list.task_set.all():
        for tag in task.tag_set.all():
           if tag not in tags:
               tags.append(tag)
    # selecting lists of the where he is the creator (job.type = 4)
    jobs = request.user.job_set.filter(type = 4)
    # creating list to store user's lists
    lists = []
    # appending this lists
    for job in jobs:
        lists.append( List.objects.get(pk = job.list_id) )
    # passing as context the lists of the user,
    # the tags that he can follow
    # and also the list that will be followed
    context = {'lists': lists, 'tags': tags, 'source': list}
    return render(request, 'appsite/follow_detail.html', context)
    
    #return HttpResponseRedirect(
        #reverse('appsite:follow_detail', args=(list.id, )))

def invite_down(request, pk):
    job = Job.objects.get(pk=pk)
    job.delete() # refusing request

    return HttpResponseRedirect(
        reverse('appsite:detail', args=(job.user_id, )))