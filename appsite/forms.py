from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import List, Task, Tag, Job
from django import forms


class ListForm(ModelForm):
    class Meta:
        model = List
        fields = [
            'name',
            'symbol',
            'picture',
            'description',
        ]
        labels = {
            'name' : 'Nome',
            'symbol' : 'Ícone',
            'picture' : 'Imagem (URL)',
            'description' : 'Descrição',
        }


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = [
            'name',
        ]
        labels = {
            'name' : 'Tarefa',
        }


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = [
            'name',
            'value'
        ]
        labels = {
            'name' : 'Coluna',
            'value' : 'Tag'
        }


class InviteForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            'user'
        ]
        labels = {
            'user' : 'Convidado'
        }


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            'user',
            'type'
        ]
        labels = {
            'user' : 'Usuário',
            'type' : 'Cargos'
        }

    def __init__(self, *args, **kwargs):
        # Extrai dados oriundos de JobUpdateView
        self.user = kwargs.pop('user')       # Usuário atual da página
        self.list_id = kwargs.pop('list_pk') # Id da lista atual

        super(JobForm, self).__init__(*args, **kwargs)

        list_obj = List.objects.get(pk=self.list_id) # Obtém a lista

        # Obtém cargo do usuário atual na lista
        job = Job.objects.get(user=self.user, list=list_obj)
        job_type = job.type

        # Obtém todos os usuários com cargos menor ou igual ao do usuário atual (exclui o criador)
        subordinates = Job.objects.filter(list=list_obj, type__lte=job_type).exclude(type=4).values('user')
        subordinates_id = subordinates.values_list('pk', flat=True)

        # Obtém todos os cargos subordinados
        inferior_jobs = [(2, 'Seguidor'), (3, 'Administrador')]

        # Seleciona apenas os usuários subordinados ao atual
        self.fields['user'].queryset = User.objects.filter(pk__in=subordinates_id)
        self.fields['type'] = forms.ChoiceField(choices=inferior_jobs)
