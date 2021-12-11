from django.forms import ModelForm
from .models import List, Task, Tag, Job


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
