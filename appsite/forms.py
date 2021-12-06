from django.forms import ModelForm
from .models import UserData, Lists, Tasks, Tags

class ListForm(ModelForm):
    model = Lists
    fields = [
        'name',
        'symbol',
        'description',
    ]
    labels = {
        'name' : 'Nome',
        'symbol' : 'Ícone',
        'description' : 'Descrição',
    }

class TaskForm(ModelForm):
    model = Tasks
    fields = [
        'name',
    ]
    labels = {
        'name' : 'Tarefa',
    }

class TagsForms(ModelForm):
    model = Tags
    fields = [
        'name',
        'value'
    ]
    labels = {
        'name' : 'Coluna',
        'value' : 'Tag'
    }
