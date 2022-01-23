from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages

from collections import defaultdict

from .models import List, Job, Tag, Follow, Task
from .forms import ListForm, TagForm, TaskForm, JobForm


# ===== #
# MIXIN #
# ===== #

class JobRequiredMixin(UserPassesTestMixin):
    # Testa se um usuário logado possui o nível de permissão mínimo
    def test_func(self):
        user = self.request.user
        list_obj = List.objects.get(pk=self.kwargs['list_id'])
        job_type = Job.objects.get(list=list_obj, user=user).type

        return job_type >= self.kwargs['level_required']

# ====== #
# CREATE #
# ====== #

class ListCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = ListForm
    template_name = 'appsite/list_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Get default context data
        context['user_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        self.object = form.save() # Saves list to the database and set it as the view's object

        # Links the creator to his list in the database
        job = Job(active_invite=False, list_id=self.object.id, user_id=self.request.user.id, type=4)
        job.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = TagForm
    template_name = "appsite/tag_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        self.object = form.save() # Saves tag to the database and set it as the view's object

        # Links the tag to it's list in the database
        list_id = self.kwargs['pk']
        list = List.objects.get(pk=list_id)
        tag = Tag.objects.get(pk=self.object.id)
        follow = Follow(list=list, tag=tag, source_id=list_id)
        follow.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('appsite:tag_create', args=(self.kwargs['pk'], ))


class TagFollowView(LoginRequiredMixin, generic.CreateView):
    template_name = 'appsite/tag_follow.html'
    form_class = TagForm # Throwable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Get default context data
        current_list = List.objects.get(pk=self.kwargs['pk'])
        current_user = self.request.user

        # Gets all lists where the current user is at least an
        # administrator and prevents a list from following itself
        jobs = Job.objects.filter(user=current_user, type__gte=3)
        lists_ids = jobs.values_list('list_id', flat=True)
        lists = List.objects.filter(pk__in=lists_ids).exclude(pk=current_list.id)

        # Gets and sorts all unique tags in list
        tags = current_list.tag_set.all().distinct()
        # Create or append to dictonary of lists
        tags_dict = defaultdict(list)
        for tag in tags:
            tags_dict[tag.name].append(tag)

        context['source_list'] = current_list
        context['source_tags'] = dict(tags_dict)
        context['user_lists']  = lists
        return context

    def post(self, request, *args, **kwargs):
        # Get form data and remove csrf token
        post_data = list( dict(request.POST.lists()).keys() )
        post_data = post_data[1: ]

        # POST validation
        if not post_data: # User selected nothing
            messages.error(request, "Selecione uma e lista e pelo menos uma tag.")
            return super().post(request, *args, **kwargs)

        elif post_data[0][0] != 'l': # User don't selected a list
            messages.error(request, "Selecione uma lista.")
            return super().post(request, *args, **kwargs)

        elif len(post_data) < 2: # User selected a list, but no tags
            messages.error(request, "Selecione pelo menos uma tag.")
            return super().post(request, *args, **kwargs)

        # Gets all ids in POST and sorts them
        ids = [int(id[1: ]) for id in post_data]
        to_list_id  = ids[0]                     # ID of destiny list
        tags_ids    = ids[1: ]                   # ID of followed tags
        src_list_id = self.kwargs['pk']          # ID of source list

        # Through IDs gets objects
        to_list = List.objects.get(pk=to_list_id)
        src_list = List.objects.get(pk=src_list_id)
        tags = Tag.objects.filter(pk__in=tags_ids) 

        # Gets all tasks in the followed list with the given tag
        for tag in tags:
            tasks = tag.task.filter(list_id=src_list_id)
            # Copies each of these tasks to destiny list if the original_id permits
            for task in tasks:
                if not to_list.task_set.filter(original_id=task.original_id):
                    task_copy = Task.objects.create(list_id=to_list_id, original_id=task.original_id, name=task.name, due_date=task.due_date, done=False)
                    task_copy.save()
                    # Links followed tags from the original task to the task_copy
                    intersection = list( set(task.tag_set.filter()) & set(tags) )
                    for tag_copy in intersection:
                        tag_copy.task.add(task_copy)

            # Links user to source list if tag hasn't been followed by him yet
            Follow.objects.get_or_create(list=to_list, tag=tag, source_id=src_list_id)

        # If user is a guest, then become a follower
        if Job.objects.filter(list=src_list, user=request.user, type=1):
            job = Job.objects.get(list=src_list, user=request.user)
            job.active_invite = False
            job.type = 2
            job.save()
        return HttpResponseRedirect( reverse_lazy('appsite:list_detail', args=(src_list_id, )) )


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = TaskForm
    template_name = 'appsite/task_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Get default context data
        context['list'] = List.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        current_list = List.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False) # Set task as the view's object with user inputed fields
        self.object.list = current_list       # Links task to current list
        self.object.save()                    # Saves task to the database
        # There's no need to set original_id because the model will handle it (see appsite/models.py)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('appsite:tag_add', args=(self.object.id, ))


class TagAddView(LoginRequiredMixin, generic.CreateView):
    template_name = 'appsite/tag_add.html'
    form_class = TaskForm # Throwable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Get default context data

        # Gets and sorts all unique tags in list
        task = Task.objects.get(pk=self.kwargs['pk'])
        current_list = List.objects.get(pk=task.list_id)
        tags = current_list.tag_set.all().distinct()
        # Create or append to dictonary of lists
        tags_dict = defaultdict(list)
        for tag in tags:
            tags_dict[tag.name].append(tag)

        context['task'] = task
        context['tags'] = dict(tags_dict)
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        # Gets form's data and removes csrf token
        post_data = list( dict(request.POST.lists()).keys() )
        post_data = post_data[1: ]

        # Gets tags from form's data
        tags_ids = [int(tag_id) for tag_id in post_data]
        tags = Tag.objects.filter(pk__in=tags_ids)

        # Links task and tags
        task = Task.objects.get(pk=self.kwargs['pk'])
        for tag in tags:
            tag.task.add(task)

        # Propagates task to other lists that follow any of these tags
        src_list = List.objects.get(pk=task.list_id)
        followers = Follow.objects.filter(tag_id__in=tags_ids, source_id=src_list.id).exclude(list_id=src_list.id).distinct()
        self.propagate_tasks(followers, task, tags)
        return HttpResponseRedirect( reverse_lazy('appsite:list_detail', args=(src_list.id, )) )

    def propagate_tasks(self, followers, task, tags):
        """
        followers: all Follow objects that relate those lists 
        task: created task
        tags: all added tags
        """

        for follow in followers:
            src_list = List.objects.get(pk=follow.source_id)
            to_list = List.objects.get(pk=follow.list_id)

            # if there's already a task in the to_list with the same original_id => return
            # otherwise => create a task with the original_id plus other fields
            if Task.objects.filter(list_id=to_list.id, original_id=task.original_id):
                return
            else:
                task_copy = Task.objects.create(
                    list_id=to_list.id,
                    original_id=task.original_id,
                    name=task.name,
                    due_date=task.due_date,
                    done=False
                )

            # Gets which tags to_list actually follows from src_list
            followed_tags_ids = Follow.objects.filter(list_id=to_list.id, source_id=src_list.id).values_list('tag_id')
            followed_tags = Tag.objects.filter(pk__in=followed_tags_ids)

            # Gets all tags available to the task in the to_list, an intersection:
            # tags that to_list follows from src_list & tags added to task
            available_tags = list( set(followed_tags) & set(tags) )

            # From available tags, gets only ones that aren't already linked to the task
            absent_tags = list( set(available_tags) - set(task_copy.tag_set.all()) )

            if absent_tags:
                for tag in absent_tags:
                    tag.task.add(task_copy)

                # Start next level of propagation
                available_tags_ids = [tag.id for tag in available_tags]       
                deeper_followers = Follow.objects.filter(tag_id__in=available_tags_ids, source_id=to_list.id).exclude(list_id=src_list.id).distinct()
                self.propagate_tasks(deeper_followers, task_copy, available_tags)
        return

# ==== #
# READ #
# ==== #

class ListDetailView(LoginRequiredMixin, generic.DetailView):
    model = List
    template_name = 'appsite/list_detail.html'
    context_object_name = 'list'

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs) # Obtém context padrão


        ### Obtém usuários da lista separados por cargo ###
        keys = [None, 'guest', 'follower', 'admin', 'creator'] # Mapeia um número para cada cargo

        for job_type in range(1, 5):            
            user_job = Job.objects.filter(list_id=self.kwargs['pk'], type=job_type) # Obtém usuários com um cargo específico
            user_id = user_job.values_list('user_id', flat=True)                    # Utiliza o cargo para obter o id do usuário

            try: # Obtém o objeto usuário atavés do id
                user = User.objects.filter(pk__in=user_id) 
            except: # Caso não existam usuários com o cargo da iteração
                user = None 

            context[keys[job_type]] = user # Atualiza context


        ### Obtém cargo do usuário logado na lista atual ###        
        current_user = self.request.user                  # Obtém o usuário logado 
        list_obj = List.objects.get(pk=self.kwargs['pk']) # Obtém lista atual

        try: # Obtém cargo do usuário na lista
            curr_user_job_type = Job.objects.get(user=current_user, list=list_obj).type
        except: # Caso usuário nem sequer pertença à lista
            curr_user_job_type = 0


        ### Obtém taks e tags da lista atual para construir a tabela ###  
        tags_obj = Tag.objects.filter(list=list_obj)
        tags_name = tags_obj.values_list('name', flat=True)

        headers = list(set(tags_name))             # Remove headers duplicados
        tasks = Task.objects.filter(list=list_obj) # Obtém todas as tarefas da lista atual

        table_data = []   
        tasks_id = []  

        for task in tasks:
            task_data = [task.id, task.done, task.name, task.due_date] # Dados obrigatórios da tarefa            
            tag_data = []                                              # Dados opcionais da tarefa
            tasks_id += [task.id]                                      # Lista à parte, ids das tasks

            for tag_name in headers:
                tag_obj = Tag.objects.filter(list=list_obj, task=task, name=tag_name)
                tag_data += [tag_obj.values_list('value', flat=True).first()] # Concatena Tag.value de cada header

            row_data = task_data + tag_data # Une dados obrigatórios e opicionais
            table_data.append(row_data)     # Adiciona linha à tabela

        ### Constrói context ###        
        keys_translate = [None, 'convidado', 'seguidor', 'administrador', 'criador'] # Cargos assim como renderizados no front

        context['current_user'] = current_user
        context['table_data'] = table_data
        context['table_header'] = ['Concluído', 'Tarefa', 'Data'] + headers
        context['curr_user_job_type'] = [curr_user_job_type, keys_translate[curr_user_job_type]] # [número_do_cargo, nome_do_cargo]
        context['tasks_id'] = tasks_id
        
        return context


class ListMenuTemplate(LoginRequiredMixin, generic.TemplateView):
    template_name = "appsite/list_menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        list_id = self.kwargs['pk']
        list_obj = List.objects.get(pk=list_id)

        user = self.request.user
        jobtype = Job.objects.get(user=user, list=list_obj).type

        context['list_id'] = list_id
        context['curr_user_jobtype'] = jobtype
        
        return context

# ====== #
# UPDATE #
# ====== #

class ListUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = List
    form_class = ListForm
    template_name = 'appsite/list_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        list_id = self.kwargs['pk']
        list_obj = List.objects.get(pk=list_id)

        user = self.request.user
        jobtype = Job.objects.get(user=user, list=list_obj).type

        context['list_id'] = list_id
        context['curr_user_jobtype'] = jobtype
        
        return context

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class InviteUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'accounts/profile/detail.html'

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
            
        return HttpResponseRedirect( reverse_lazy('accounts:profile_detail', args=(self.kwargs['pk'], )) )


class InviteUpdateAllView(LoginRequiredMixin, generic.UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'accounts/profile/detail.html'

    def post(self, request, *args, **kwargs):
        # Obtém dados do formulário (frontend)
        post_data = dict(request.POST.lists()).keys()
        post_data = list(post_data)[1:]

        response = post_data[0]

        user = User.objects.get(pk=self.kwargs['pk'])
        jobs = Job.objects.filter(user=user, active_invite = True)

        if response == 'accept':  
            for job in jobs:
                job.active_invite = False
                job.save()          
        elif response == 'refuse':
            jobs.delete()
        else:
            pass
            
        return HttpResponseRedirect( reverse_lazy('accounts:profile_detail', args=(self.kwargs['pk'], )) )


class JobUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'appsite/job_update.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)             # Obtém context padrão
        context['list'] = List.objects.get(pk=self.kwargs['pk']) # Adiciona lista ao context

        return context

    def get_form_kwargs(self):
        # Atualiza os kwargs do formulário com os dados da requisição,
        # permitindo filtrar os dados do formulário (vide forms.py)
        kwargs = super(JobUpdateView, self).get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'list_pk':self.kwargs['pk']
        })

        return kwargs

    def post(self, request, *args, **kwargs):
        ### Lida com o convite de novos usuários para a lista ###
        post_data = request.POST
        list_obj = List.objects.get(pk=self.kwargs['pk'])

        print(post_data)

        # Trata requisições do tipo "Convidar"
        if 'invite' in post_data.keys():
            username = post_data['invite']

            if username == "": # Verifica se foi digitado um username
                messages.error(request, f"Digite uma nome de usuário para convidar.")
                return super().post(request, *args, **kwargs)

            try: # Verifica se o usuário existe
                user = User.objects.get(username=username)
            except:
                messages.error(request, f"O usuário '{username}' não existe.")
                return super().post(request, *args, **kwargs)
            
            if user in list_obj.user.all(): # Verifica se o usuário faz parte da lista
                messages.error(request, f"O usuário '{username}' já faz parte dessa lista.")
                return super().post(request, *args, **kwargs)
            else:
                Job.objects.create(user=user, list=list_obj, active_invite=True, type=1)
                messages.success(request, f"O usuário '{username}' recebeu um convite!")
                return super().post(request, *args, **kwargs)
        
        # Trata requisições do tipo "Gerenciar"
        else:
            target_id = post_data['user'] # ID do usuário a ter o cargo modificado
            new_job = post_data['type']   # Novo cargo (pode ser igual ao atual)

            target = User.objects.get(pk=target_id)

            # Atualiza o cargo
            job = Job.objects.get(user=target, list=list_obj)
            job.type = new_job
            job.save()

            return HttpResponseRedirect( reverse_lazy('appsite:list_detail', args=(self.kwargs['pk'], )) )

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'appsite/task_update.html'

    def post(self, request, *args, **kwargs):
        post_data = dict(request.POST)
        post_data.pop('csrfmiddlewaretoken')

        task_id = int( list(post_data.keys())[0] )
        task = Task.objects.get(pk=task_id)

        # Atualização dos campos da tarefa
        if 'name' in post_data or 'due_date' in post_data:
            task.name = post_data['name'][0]
            task.due_date = post_data['due_date_day'][0]   + '/' + \
                            post_data['due_date_month'][0] + '/' + \
                            post_data['due_date_year'][0]
            task.save()

        # Atualização apenas do status da tarefa
        else:            
            status = bool(int( list(post_data.values())[0][0] ))            
            task.done = status
            task.save()

        list_id = List.objects.get(task=task).pk

        return HttpResponseRedirect(reverse('appsite:list_detail', args=(list_id, )))

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)

         task_id = self.kwargs['pk']
         task = Task.objects.get(pk=task_id)

         list_id = List.objects.get(task=task).id

         context['task_id'] = task_id
         context['list_id'] = list_id

         return context

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(Task.objects.get(pk = self.kwargs['pk']).list_id, ))

# ====== #
# DELETE #
# ====== #

class ListDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = List
    template_name = 'appsite/list_delete.html'

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)        
        context['list_id'] = self.kwargs['pk']
        return context

    def get_success_url(self):
        Follow.objects.filter(source_id = self.kwargs['pk']).delete()
        Follow.objects.filter(list_id = self.kwargs['pk']).delete()
        Task.objects.filter(list_id=self.kwargs['pk']).delete()
        Job.objects.filter(list_id=self.kwargs['pk']).delete()
        return reverse_lazy('accounts:profile_detail', args=(self.request.user.id, ))


class ListUntrackView(LoginRequiredMixin, generic.DeleteView):
    model = Follow
    #form_class = JobForm
    template_name = 'appsite/list_untrack.html'

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs)
        context['list_id'] = self.kwargs['pk']
        return context

    def get_success_url(self):
        Follow.objects.filter(
            source_id=self.kwargs['pk'],
            list_id__in=self.request.user.list_set.values_list('id', flat=True)
        ).delete()

        Job.objects.get(list_id=self.kwargs['pk'], user_id=self.request.user).delete()

        return reverse_lazy('accounts:profile_detail', args=(self.request.user.id, ))


class TagUnfollowView(LoginRequiredMixin, generic.UpdateView):
    model = List
    form_class = ListForm
    template_name = 'appsite/tag_unfollow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        follows = Follow.objects.filter(list_id=self.kwargs['pk'])

        # Creating a list of objects like [tag, list, follow] to unpack the three together
        # in the front-end, in order to obtain: tag.name, list.name and follow.id
        follows_list = []
        for follow in follows:
            follows_list.append([Tag.objects.get(pk=follow.tag_id), List.objects.get(pk=follow.source_id), follow])
        
        # Passing this list of lists in context (to the front)
        context['follows_list'] = follows_list

        return context

    def post(self, request, *args, **kwargs):
        # Obtém dados do formulário (frontend)
        post_data = dict(request.POST)
        post_data.pop('csrfmiddlewaretoken')

        # Deleting selected follows_objects
        follow_ids = [int(id) for id in list(post_data.keys())]
        Follow.objects.filter(pk__in=follow_ids).delete()
        
        list_id = self.kwargs['pk']
        # Redirecting to lists's page
        return HttpResponseRedirect(reverse_lazy('appsite:list_detail', args=(list_id, )))


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = 'appsite/task_delete.html'

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)

         task_id = self.kwargs['pk']
         task = Task.objects.get(pk=task_id)

         list_id = List.objects.get(task=task).id

         context['task_id'] = task_id
         context['list_id'] = list_id

         return context

    def get_success_url(self):
        task_id = self.kwargs['pk']
        task = Task.objects.get(pk=task_id)
        list_id = List.objects.get(task=task).id

        return reverse_lazy('appsite:list_detail', args=(list_id, ))
