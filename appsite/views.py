from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from collections import defaultdict

from .models import List, Job, Tag, Follow, Task
from .forms import ListForm, TagForm, TaskForm, JobForm


# ====== #
# CREATE #
# ====== #

class ListCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'appsite/list_create.html'
    form_class = ListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Gets default context data
        context['user_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        self.object = form.save() # Saves the list to the database and set it as the view's object

        # Links the creator to his list in the database
        job = Job(active_invite=False, list_id=self.object.id, user_id=self.request.user.id, type=4)
        job.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "appsite/tag_create.html"
    form_class = TagForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_id'] = self.kwargs['pk']
        return context

    def form_valid(self, form):
        self.object = form.save() # Saves the tag to the database and set it as the view's object

        # Links the tag to its list in the database
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
        context = super().get_context_data(**kwargs) # Gets default context data
        current_list = List.objects.get(pk=self.kwargs['pk'])
        current_user = self.request.user

        # Gets all lists where the current user is at least an
        # administrator and prevents a list from following itself
        jobs = Job.objects.filter(user=current_user, type__gte=3)
        lists_ids = jobs.values_list('list_id', flat=True)
        lists = List.objects.filter(pk__in=lists_ids).exclude(pk=current_list.id)

        # Gets and sorts all unique tags in list
        tags = current_list.tag_set.all().distinct()
        # Dictionary of lists: create or append
        tags_dict = defaultdict(list)
        for tag in tags:
            tags_dict[tag.name].append(tag)

        context['source_list'] = current_list
        context['source_tags'] = dict(tags_dict)
        context['user_lists']  = lists
        return context

    def post(self, request, *args, **kwargs):
        # Gets the form's data and removes csrf token
        post_data = list( dict(request.POST.lists()).keys() )
        post_data = post_data[1: ]

        # POST validation
        if not post_data: # The user selected nothing
            messages.error(request, "Selecione uma e lista e pelo menos uma tag.")
            return super().post(request, *args, **kwargs)

        elif post_data[0][0] != 'l': # The user doesn't select a list
            messages.error(request, "Selecione uma lista.")
            return super().post(request, *args, **kwargs)

        elif len(post_data) < 2: # The user selected a list, but no tags
            messages.error(request, "Selecione pelo menos uma tag.")
            return super().post(request, *args, **kwargs)

        # Gets all ids in POST and sorts them
        ids = [int(id[1: ]) for id in post_data]
        to_list_id  = ids[0]                     # The ID of destiny list
        tags_ids    = ids[1: ]                   # The IDs of followed tags
        src_list_id = self.kwargs['pk']          # The ID of source list

        to_list = List.objects.get(pk=to_list_id)
        src_list = List.objects.get(pk=src_list_id)
        tags = Tag.objects.filter(pk__in=tags_ids) 

        # Gets all tasks in the followed list with the given tag
        for tag in tags:
            tasks = tag.task.filter(list_id=src_list_id)
            # Copies each of these tasks to the destiny list if the original_id permits
            for task in tasks:
                if not to_list.task_set.filter(original_id=task.original_id):
                    task_copy = Task.objects.create(list_id=to_list_id, original_id=task.original_id, name=task.name, due_date=task.due_date, done=False)
                    task_copy.save()
                    # Links the followed tags from the original task to the task_copy
                    intersection = list( set(task.tag_set.filter()) & set(tags) )
                    for tag_copy in intersection:
                        tag_copy.task.add(task_copy)

            # Links user to source list if the tag hasn't been followed by him yet
            Follow.objects.get_or_create(list=to_list, tag=tag, source_id=src_list_id)

        # If the user is a guest, then becomes a follower
        if Job.objects.filter(list=src_list, user=request.user, type=1):
            job = Job.objects.get(list=src_list, user=request.user)
            job.active_invite = False
            job.type = 2
            job.save()
        return HttpResponseRedirect( reverse_lazy('appsite:list_detail', args=(src_list_id, )) )


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = 'appsite/task_create.html'
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Gets default context data
        context['list'] = List.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        current_list = List.objects.get(pk=self.kwargs['pk'])
        self.object = form.save(commit=False) # Set the task as the view's object along with user-inputted fields
        self.object.list = current_list       # Links the task to the current list
        self.object.save()                    # Saves the task to the database
        # There's no need to set the original_id because the task's model will handle it (see appsite/models.py)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('appsite:tag_add', args=(self.object.id, ))


class TagAddView(LoginRequiredMixin, generic.CreateView):
    template_name = 'appsite/tag_add.html'
    form_class = TaskForm # Throwable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Gets default context data

        # Gets and sorts all unique tags in list
        task = Task.objects.get(pk=self.kwargs['pk'])
        current_list = List.objects.get(pk=task.list_id)
        tags = current_list.tag_set.all().distinct()
        # Dictionary of lists: create or append
        tags_dict = defaultdict(list)
        for tag in tags:
            tags_dict[tag.name].append(tag)

        context['task'] = task
        context['tags'] = dict(tags_dict)
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        # Gets the form's data and removes csrf token
        post_data = list( dict(request.POST.lists()).keys() )
        post_data = post_data[1: ]

        # Gets the tags from the form's data
        tags_ids = [int(tag_id) for tag_id in post_data]
        tags = Tag.objects.filter(pk__in=tags_ids)

        # Links the task and the tags
        task = Task.objects.get(pk=self.kwargs['pk'])
        for tag in tags:
            tag.task.add(task)

        # Propagates the task to other lists that follow any of these tags
        src_list = List.objects.get(pk=task.list_id)
        followers = Follow.objects.filter(tag_id__in=tags_ids, source_id=src_list.id).exclude(list_id=src_list.id).distinct()
        self.propagate_tasks(followers, task, tags)
        return HttpResponseRedirect( reverse_lazy('appsite:list_detail', args=(src_list.id, )) )

    def propagate_tasks(self, followers, task, tags):
        """
        Custom recursive method responsible to deep copy a task to its followers, based on the added tags.

            Params:
                followers (QuerySet): all unique Follow instances that relate a source list to its followers
                task      (QuerySet): the Task instance which had tags added to
                tags      (QuerySet): all added Tag instances
            Retuns:
                None
        """
        for follow in followers:
            print(type(followers), type(task), type(tags))
            src_list = List.objects.get(pk=follow.source_id)
            to_list = List.objects.get(pk=follow.list_id)

            # If there's already a task in the to_list with the same original_id => Returns
            # Otherwise => Creates a task with the original_id plus the other fields
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

            # Gets which tags the to_list actually follows from src_list
            followed_tags_ids = Follow.objects.filter(list_id=to_list.id, source_id=src_list.id).values_list('tag_id')
            followed_tags = Tag.objects.filter(pk__in=followed_tags_ids)

            # Gets all tags available to the task in the to_list, an intersection:
            # tags that to_list follows from src_list & tags added to the task
            available_tags = list( set(followed_tags) & set(tags) )

            # From available tags, gets only ones that aren't already linked to the task
            absent_tags = list( set(available_tags) - set(task_copy.tag_set.all()) )
            if absent_tags:
                for tag in absent_tags:
                    tag.task.add(task_copy)

            # Starts next level of propagation
            available_tags_ids = [tag.id for tag in available_tags]
            deeper_followers = Follow.objects.filter(tag_id__in=available_tags_ids, source_id=to_list.id).exclude(list_id=src_list.id).distinct()
            self.propagate_tasks(deeper_followers, task_copy, available_tags)
        return

# ==== #
# READ #
# ==== #

class ListDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'appsite/list_detail.html'
    context_object_name = 'list'
    model = List

    def get_context_data(self, **kwargs):        
        context = super().get_context_data(**kwargs) # Gets default context data

        ### Gets the list's users sorted by job ###
        jobs_map = {
            1 : 'guest',
            2 : 'follower',
            3 : 'administrator',
            4 : 'creator'
        }

        for job_num in jobs_map.keys():
            # Gets all users IDs with a given job
            users_ids = Job.objects.filter(list_id=self.kwargs['pk'], type=job_num).values_list('user_id', flat=True)

            # Gets the users objects or None if there's no user with the given job
            if users_ids:
                users = User.objects.filter(pk__in=users_ids)
            else:
                users = None

            context[jobs_map[job_num]] = users

        ### Gets the current user job in the list ###
        current_user = self.request.user
        current_list = List.objects.get(pk=self.kwargs['pk'])

        try:
            current_user_job_type = Job.objects.get(user=current_user, list=current_list).type
        except: # The user actually isn't in the list
            current_user_job_type = 0

        context['current_user'] = {
            'object'   : current_user,
            'job_type' : {
                'code' : current_user_job_type,
                'name' : jobs_map[current_user_job_type]
            }
        }

        ### Gets and sorts tasks and tags from current list to build the list's table ###
        tags_names = Tag.objects.filter(list=current_list).values_list('name', flat=True)

        # Prevents duplicates in the table header
        table_header = list(set(tags_names))
        tasks = Task.objects.filter(list=current_list)

        table_body = []
        for task in tasks:
            task_data = [task.id, task.done, task.name, task.due_date] # Mandatory task data
            tag_data  = []                                             # Optional task data (aka tag data)
            # Concatenates tag's value in the same order that tag's name appears in headers
            for tag_name in table_header:
                try:
                    tag_data += [Tag.objects.get(list=current_list, task=task, name=tag_name).value]
                except ObjectDoesNotExist: # In case the task doesn't have the tag
                    tag_data += ['------']

            row_data = task_data + tag_data
            table_body.append(row_data)

        context['table_body']   = table_body
        context['table_header'] = ['Done', 'Task', 'Date'] + table_header

        ### Gets the tasks IDs (needed for jQuery functions in frontend) ###
        context['tasks_ids'] = list(tasks.values_list('id', flat=True))
        return context


class ListMenuTemplate(LoginRequiredMixin, generic.TemplateView):
    template_name = "appsite/list_menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_list = List.objects.get(pk=self.kwargs['pk'])
        job_type = Job.objects.get(user=self.request.user, list=current_list).type

        context['list'] = current_list
        context['current_user'] = {
            'job_type' : {
                'code' : job_type
            }
        }
        return context

# ====== #
# UPDATE #
# ====== #

class ListUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'appsite/list_update.html'
    context_object_name = 'list'
    form_class = ListForm
    model = List

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_list = List.objects.get(pk=self.kwargs['pk'])
        job_type = Job.objects.get(user=self.request.user, list=current_list).type

        context['current_user'] = {
            'job_type' : {
                'code' : job_type
            }
        }
        return context

    def get_success_url(self):
        return reverse_lazy('appsite:list_detail', args=(self.object.id, ))


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'appsite/task_update.html'
    context_object_name = 'task'
    form_class = TaskForm
    model = Task

    def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)

         list_id = Task.objects.get(pk=self.kwargs['pk']).list_id

         context['list'] = List.objects.get(pk=list_id)
         return context

    def post(self, request, *args, **kwargs):
        # Gets the form's data
        post_data = request.POST.dict()
        print(post_data)

        task_id = int( list(post_data.keys())[1] )
        task = Task.objects.get(pk=task_id)

        # The user wants to update task name and/or due date
        if 'name' in post_data.keys():
            task.name = post_data['name']
            task.due_date = post_data['due_date_day']   + '/' + \
                            post_data['due_date_month'] + '/' + \
                            post_data['due_date_year']
            task.save()
        # The user checked or unchecked a task's done field
        else:
            new_status = int(post_data[str(task_id)])
            task.done = new_status
            task.save()

        list_id = List.objects.get(task=task).id
        return HttpResponseRedirect( reverse('appsite:list_detail', args=(list_id, )) )


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
