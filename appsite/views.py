from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages

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
    form_class = TagForm

    # Exibir (tag.name) e (tag.value) da lista a ser seguida
    # Exibir todas as listas em que o usuário é criador

    def get_context_data(self, **kwargs):
        current_user = self.request.user

        # Obtém todas as listas em que o usuário atual é pelo menos admistrador
        jobs = Job.objects.filter(user=current_user, type__gte=3)
        lists_id = jobs.values_list('list_id', flat=True)
        lists = List.objects.filter(pk__in=lists_id)

        # Obtém a lista atual
        list = List.objects.get(pk=self.kwargs['pk'])

        # Obtém todas as tags da lista
        tags = list.tag_set.all().distinct()

        context = {
            'source': list,
            'user_allowed_lists' : lists,
            'source_tags' : tags
        }

        return context
    
    def post(self, request, *args, **kwargs):
        # Obtém dados do formulário e remove token
        post_data = list( dict(request.POST.lists()).keys() )
        post_data = post_data[1:]

        # Validação do POST
        if not post_data: # Usuário não selecionou nada
            messages.error(request, "Selecione uma e lista e pelo menos uma tag.")
            return super().post(request, *args, **kwargs)

        elif post_data[0][0] != 'l': # Usuário não selecionou uma lista
            messages.error(request, "Selecione uma lista.")
            return super().post(request, *args, **kwargs)

        elif len(post_data) < 2: # Usuário selecionou uma lista, mas não uma tag
            messages.error(request, "Selecione pelo menos uma tag.")
            return super().post(request, *args, **kwargs)

        # Recorta o valor numérico dos ids de lista e tag
        ids = [int(id[1:]) for id in post_data]

        list_id = ids[0]              # ID da lista de destino
        tags_id = ids[1:]             # ID das tags seguidas
        source_id = self.kwargs['pk'] # ID da lista seguida

        list_obj = List.objects.get(pk=list_id)
        source_obj = List.objects.get(pk=source_id)
        tags = Tag.objects.filter(pk__in=tags_id) 

        for tag in tags:
            # Getting all tasks that have the tag and come from the followed list
            tasks = tag.task.filter(list_id=source_id)
            # Adding each of these tags to the user's list
            for task in tasks:
                # Checking if the task is originally from the destination list
                if list_obj.task_set.filter(original_id=task.original_id):
                    pass # Skip them
                else:
                    # Adding the task to the list
                    task_copy = Task.objects.create(list_id=list_id, original_id=task.original_id, name=task.name, due_date=task.due_date, done=False)
                    task_copy.save()
                    # Linking all the tags of the task that are followed to this newly created task (task_copy)
                    for tag_copy in [task_og for task_og in task.tag_set.filter() if task_og in tags]:
                        tag_copy.task.add(task_copy)
        
            # Creating new follow object of following list, tag being followed and followed list id
            # checking if the user has already followed the tag (from the same source_id) with the same list
            if ( Follow.objects.filter(list=List.objects.get(pk=list_id), tag=Tag.objects.get(pk=tag.id), source_id=source_id) ):
                pass
            else:
                follow = Follow.objects.create(list=List.objects.get(pk=list_id), tag=Tag.objects.get(pk=tag.id), source_id=source_id)
        
        # Updating user's permission to follower and removing list invite
        if Job.objects.filter(list=source_obj, user=request.user, type__gte=2):
            pass # Skip job update to follower if user isn't a guest
        else:
            job = Job.objects.get(list=source_obj, user=request.user)
            job.active_invite = False
            job.type=2
            job.save()

        # Redirecting to user's page
        return HttpResponseRedirect(reverse_lazy('appsite:list_detail', args=(source_id, )))

# This is the function responsible for adding a new task to a list
def task_create(request, **kwargs):
    # Getting the object that the new task will be created in
    list_id = kwargs['pk']
    list = get_object_or_404(List, pk=list_id)

    if request.method == 'POST': # If request method is POST (sent from the form)
        form = TaskForm(request.POST)
        if form.is_valid():

            # Getting the data form the form 
            task_name = form.cleaned_data['name']
            due_date = form.cleaned_data['due_date']

            # Original_id can now be NULL, so task_new is created without an original id
            task_new = Task.objects.create(name=task_name, list_id=list_id, due_date=due_date)

            # And then the original id is provided to the new task and the task is saved on the database
            task_new.original_id = task_new.id
            task_new.save()

            # Redirecting to the view that will be responsible for adding tags to this new task
            return HttpResponseRedirect(reverse_lazy('appsite:tag_add', args=(task_new.id, )))

    else: # If request method is not POST

        # The form that will be rendered in the page
        form = TaskForm()

    # Loading the page of task creation (a generic form)
    context = {'form': form, 'list': list}
    return render(request,'appsite/task_create.html', context)


# Read tag_add first and then return here
def task_recurrent(follows,task_new, tags_add):
    # Iterating over each list the follows mother-list
    for follow in follows:

        # Getting the id of mother-list:
        source_id = task_new.list_id

        # Getting one of the child-lists that the mother-list provided
        list_child = get_object_or_404(List, pk = follow.list_id)

        # Seeing if the task is original
        task_filter = list_child.task_set.filter(original_id=task_new.original_id)
        
        if (task_filter):           
            task2_new = Task.objects.get(original_id = task_new.original_id, list_id = list_child.id) # Not adding tasks that share the same original_id
        
        else:            
            # Adding the task to the list: now task_new refers to the task created on the child-list
            # ( this is useful to shorten the length of the code )
            task2_new = Task.objects.create(list_id=list_child.id, original_id=task_new.original_id, name=task_new.name, due_date=task_new.due_date, done=False)
            task2_new.save()
            
        # Finding the tags that the child list follow from the mother-list
        temp_child_follows = Follow.objects.filter(list_id = list_child, source_id = source_id)
        tags_child_follows = [Tag.objects.get(pk = follow.tag_id) for follow in temp_child_follows]
        
        # Filtering the tags that the new task from mother-list has AND this new list follows from the mother-list
        tags_filtered = [tag for tag in tags_child_follows if (tag in tags_add)]
        # Getting the ids of these filtered tasks
        tags_filtered_id = [tag.id for tag in tags_filtered]
        # Finding the tags that have not been added yet to the new task
        tags_filtered_new = [tag for tag in tags_filtered if tag not in task2_new.tag_set.all()]

        if (tags_filtered_new):
            # Linking the filtered tags that haven't been linked yet to this newly created task
            for tag in tags_filtered_new:
                tag.task.add(task2_new)
        
            # Finding the lists that follow the tags of the new created task from child list
            follows2 = Follow.objects.filter(tag_id__in = tags_filtered_id, source_id = list_child.id).distinct()
        
            # Continuing the recurrence
            task_recurrent(follows2, task2_new, tags_filtered)

    return True

# Add tags to new task 
class TagAddView(LoginRequiredMixin, generic.CreateView):
    
    # Basic generic class initial lines 
    template_name = 'appsite/tag_add.html'
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        # Getting the new task from the pk passed in the URL
        task_new = Task.objects.get(pk = self.kwargs['pk'])
        
        # Getting the mother-list of this task
        source = List.objects.get(pk = task_new.list_id)
        
        # Getting the tags that this mother-list follows
        tags = source.tag_set.all().distinct()

        # Getting the current user making the request
        user = self.request.user

        context = {
            'task': task_new,
            'tags' : tags,
            'user' : user
        }

        return context

    def post(self, request, *args, **kwargs):

        # Obtém dados do formulário (frontend)
        post_data = dict(request.POST.lists())
        post_data.pop('csrfmiddlewaretoken')

        print(post_data)

        # Getting tags selected to be added in the task from the dict passed on POST requisition
        tags_id = [int(id[1:]) for id in list(post_data.keys())]
        tags_add = Tag.objects.filter(pk__in=tags_id) 

        # Getting the new task
        task_new = Task.objects.get(pk = self.kwargs['pk'])

        # Getting the mother-list
        source = List.objects.get(pk = task_new.list_id)

        # Adding the new task and the tags together:
        for tag in tags_add:
            tag.task.add(task_new)

        # Getting all the lists that follow at least one of the tags of new task
        follows = Follow.objects.filter(tag_id__in = tags_id, source_id = source.id).distinct()

        # Starting the recursion
        task_recurrent(follows,task_new, tags_add)

        return HttpResponseRedirect(reverse_lazy('appsite:list_detail', args=(source.id, )))
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
