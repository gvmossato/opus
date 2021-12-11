from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .models import List, Job, Tag, Follow, Task
from .forms import ListForm, InviteForm, JobForm, TagForm, TaskForm

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


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = TagForm
    template_name = "appsite/tag_create.html"

    def get_success_url(self):       
        # Obtém lista em que foi criada a tag
        list_id = self.kwargs['pk']
        list = List.objects.get(pk=list_id)

        # Obtém tag recém criada  
        tag = Tag.objects.get(pk=self.object.id)
        
        # Linka a mova tag com a lista, através de Follow
        follow = Follow(list=list, tag=tag, source_id=list_id)
        follow.save()
        return reverse_lazy('appsite:list_detail', args=(list_id, ))


class TagFollowView(LoginRequiredMixin, generic.CreateView):
    template_name = 'appsite/tag_follow.html'
    form_class = TagForm

    # Exibir (tag.name) e (tag.value) da lista a ser seguida
    # Exibir todas as listas em que o usuário é criador

    def get_context_data(self, **kwargs):
        current_user = self.request.user
        jobs = Job.objects.filter(user=current_user, type__gte=3)
        lists_id = jobs.values_list('list_id', flat=True)
        lists = List.objects.filter(pk__in=lists_id)

        # Obtém a lista atual
        list = List.objects.get(pk=self.kwargs['pk'])

        # Obtém todas as tagas da lista
        tags = Tag.objects.filter(list=list)

        context = {
            'source': list,
            'user_allowed_lists' : lists,
            'source_tags' : tags
        }

        return context
    
    def post(self, request, *args, **kwargs):
        # Obtém dados do formulário (frontend)
        post_data = dict(request.POST.lists())
        post_data.pop('csrfmiddlewaretoken')

        ids = [int(id) for id in list(post_data.keys())]

        list_id = ids[0]
        tags_id = ids[1:]
        source_id = self.kwargs['pk']

        list_obj = get_object_or_404(List,pk=list_id)
        source_obj = get_object_or_404(List,pk=source_id)
        tags = Tag.objects.filter(pk__in=tags_id) 

        for tag in tags:
            # Getting all tasks that have the tag and come from the followed list
            tasks = tag.task.filter(list_id=source_id)
            # Adding each of these tags to the user's list
            for task in tasks:
                # Checking if the task is original in the list of destination
                if list_obj.task_set.filter(original_id=task.original_id):
                    pass # Not adding tasks that share the same original_id
                else:
                    # Adding the task to the list
                    task_copy = Task.objects.create(list_id=list_id, original_id=task.original_id, name =task.name, done=False)
                    task_copy.save()
                    # Linking all the tags of the task that are followed
                    # to this newly created task (task_copy)
                    for tag_copy in [task_og for task_og in task.tag_set.filter() if task_og in tags]:
                        tag_copy.task.add(task_copy)
        
            # Creating new follow object of following list, tag being followed and followed list id
            # checking if the user has already followed the list with the same list
            if Follow.objects.filter(list=List.objects.get(pk=list_id), tag=Tag.objects.get(pk=tag.id), source_id=source_id):
                pass
            else:
                follow = Follow(list=List.objects.get(pk=list_id), tag=Tag.objects.get(pk=tag.id), source_id=source_id)
                follow.save()
        
        # Updating user's permission to follower and removing list invite
        #job = Job.objects.get(list_id=source_id, user_id=request.user.id)
        if Job.objects.filter(list=source_obj, user=request.user):
            pass
        else:
            job = Job.objects.create(list=source_obj, user=request.user, active_invite= False, type=2)
            job.save()

        # Redirecting to user's page
        return HttpResponseRedirect(reverse_lazy('appsite:list_detail', args=(source_id, )))


# TASK CREATION
#
# The code below is not easy to understand, but I will try to do my best
# to explain it to you, dear reader
#
# Three functions are necessary in order for the task creation to successful:
# task_create is the most basic one and just creates the task in the mother-list,
# tag_add is also simple and just add the tag(s) (each tag added calls this function once),
# that were specified in the creation proccess of the task.
#
# Task_recurrent is the hardest one: it will create a copy of the task created, as well its tags
# in each list that follows the mother list.
#
# But then, once the child_lists have the new task, it will copy the task and its tags
# to the lists that follow the child_lists and so on. The algorithm stops when it reaches 
# a point where not list follows the current list being analyzed.

def task_create(request, list_id):
    list = get_object_or_404(List, pk=list_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_name = form.cleaned_data['name']
            # original_id can now be NULL, so task_new is created without an original id
            task_new = Task.objects.create(name = task_name, list_id = list_id)
            # And then the original id is provided to the new task
            task_new.original_id = task_new.id
            task_new.save()
            # Listing all tags in mother-list (its importatn so we can list the tags in tag_add.html)
            tags = list.tag_set.all()
            context = {'task':task_new, 'tags':tags, 'user': request.user}
            return render(request, 'appsite/tag_add.html', context)
    else:
        form = TaskForm()
    context = {'form': form, 'list': list}
    return render(request,'appsite/task_create.html', context)

# Read tag_add first and then return here
def task_recurrent(follows,task_new, tag):
    for follow in follows:
        # getting one of the child-lists of the mother-list provided
        list_child = get_object_or_404(List, pk = follow.list_id)
        # seeing if the task is original
        task_filter = list_child.task_set.filter(original_id=task_new.original_id)
        if (task_filter):
            pass # Not adding tasks that share the same original_id
        else:
            # Adding the task to the list
            task2_new = Task.objects.create(list_id=list_child.id, original_id = task_new.original_id, name = task_new.name, done = task_new.done)
            task2_new.save()
            # Linking the tag to this newly created task
            tag.task.add(task2_new)
            # finding the lists that follow
            follows2 = tag.follow_set.filter(source_id = list_child.id)
            task_recurrent(follows2, task2_new, tag)
    return True


# giving a of mother-list tag to the new created task
def tag_add(request, task_id, tag_id):
    # getting the object of the new created task (in mother-list)
    task_new = get_object_or_404(Task, pk=task_id)
    # getting the object for mother-list
    list = get_object_or_404(List, pk=task_new.list_id)
    # getting the tag to be added 
    tag = get_object_or_404(Tag, pk=tag_id)
    # adding new task and tag together
    tag.task.add(task_new)
    
    # recurrently adding created task to all lists that follow mother-lists' tag
    follows = tag.follow_set.filter(source_id = list.id)
    # entering in task_recurrent function, let's go there ^
    task_recurrent(follows,task_new, tag)

    tags = list.tag_set.all()
    context = {'task': task_new, 'tags': tags, 'user': request.user}
    return render(request, 'appsite/tag_add.html', context)

# ==== #
# READ #
# ==== #

class UserDetailView(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = 'appsite/detail.html'

    # Envia para o template:
    # - Qual usuário está logado e qual perfil foi acessado
    # - As listas do perfil acessado
    def get_context_data(self, **kwargs):        
        current_user = self.request.user
        profile_user = User.objects.get(pk=self.kwargs['pk'])

        lists_id_pending = Job.objects.filter(user=profile_user, active_invite=True).values_list('list')
        lists_id_confirmed = Job.objects.filter(user=profile_user, active_invite=False).values_list('list')

        lists_pending = List.objects.filter(pk__in=lists_id_pending)
        lists_confirmed = List.objects.filter(pk__in=lists_id_confirmed)
          
        context = {
            'current_user'    : current_user,
            'profile_user'    : profile_user,
            'lists_pending'   : lists_pending,
            'lists_confirmed' : lists_confirmed
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

        # Obtém o usuário logado
        current_user = self.request.user
        context['current_user'] = current_user

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


class InviteUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'appsite/detail.html'

    def post(self, request, *args, **kwargs):
        # Obtém dados do formulário (frontend)
        post_data = dict(request.POST.lists()).keys()
        post_data = list(post_data)[1:]

        response, list_id = post_data

        list_obj = List.objects.get(pk=list_id)
        user = User.objects.get(pk=self.kwargs['pk'])

        job = Job.objects.get(user=user, list=list_obj)

        if response == 'accept':
            job.active_invite = False
            job.save()                    
        elif response == 'refuse':
            job.delete()
        else:
            pass
            
        return HttpResponseRedirect( reverse_lazy('appsite:detail', args=(self.kwargs['pk'], )) )

    # def get_success_url(self):
    #     return reverse_lazy('appsite:detail', args=(self.object.id, ))
