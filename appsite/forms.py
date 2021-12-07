from django.forms import ModelForm
from .models import UserData, Lists, Tasks, Tags


class UserDataForm(ModelForm):
    class Meta:
        model = UserData
        fields = [
            'picture'
        ]
        labels = {
            'picture' : 'Foto (URL)'
        }

class ListForm(ModelForm):
    class Meta:
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
    class Meta:
        model = Tasks
        fields = [
            'name',
        ]
        labels = {
            'name' : 'Tarefa',
        }

class TagsForms(ModelForm):
    class Meta:
        model = Tags
        fields = [
            'name',
            'value'
        ]
        labels = {
            'name' : 'Coluna',
            'value' : 'Tag'
        }
