import requests
from django.contrib.auth.models import User
from django.forms import ModelForm, widgets
from .models import List, Task, Tag, Job, Profile
from django import forms


class ListForm(ModelForm):
    class Meta:
        model = List
        fields = [
            'name',
            'symbol',
            'picture',
            'description',
            'color',
        ]
        labels = {
            'name' : 'Nome',
            'symbol' : 'Ícone',
            'color' : 'Cor',
            'picture' : 'Imagem (URL)',
            'description' : 'Descrição',
        }
        widgets = {
            "color": widgets.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super(ListForm, self).__init__(*args, **kwargs)
        self.fields['picture'].initial = requests.get('https://source.unsplash.com/1920x1080/?work').url


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = [
            'name',
            'due_date'
        ]
        labels = {
            'name' : 'Tarefa',
            'due_date' : 'Entrega'
        }
        widgets = {
            "due_date": forms.SelectDateWidget(),
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
        # Extrai dados enviados pela JobUpdateView
        self.user = kwargs.pop('user')       # Usuário atual da página
        self.list_id = kwargs.pop('list_pk') # Id da lista atual

        super(JobForm, self).__init__(*args, **kwargs)

        list_obj = List.objects.get(pk=self.list_id) # Obtém a lista atual
        
        # Obtém todos os ids de seguidores e administradores
        subordinates_job = Job.objects.filter(list=list_obj, type__in=[2, 3])
        subordinates_id = subordinates_job.values_list('user', flat=True)

        # Define as transições de cargo possíveis
        jobs_transitions = [(2, 'Seguidor'), (3, 'Administrador')]

        # Seleciona apenas os usuários subordinados
        self.fields['user'].queryset = User.objects.filter(pk__in=subordinates_id)
        self.fields['type'] = forms.ChoiceField(choices=jobs_transitions)

        
class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'picture',
            'description'
        ]
        labels = {
            'picture' : 'Foto (URL)',
            'type' : 'Descrição'
        }
