from django.forms import ModelForm
from .models import List, Task, Tag


#class UserDataForm(ModelForm):
#    class Meta:
#        model = UserData
#        fields = [
#            'picture'
#        ]
#        labels = {
#            'picture' : 'Foto (URL)'
#        }

class ListForm(ModelForm):
    class Meta:
        model = List
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
        model = Task
        fields = [
            'name',
        ]
        labels = {
            'name' : 'Tarefa',
        }

class TagsForms(ModelForm):
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
