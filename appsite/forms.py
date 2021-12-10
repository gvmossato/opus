from django.forms import ModelForm
from .models import List, Task, Tag, Job


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

#class TagForm(ModelForm):
 #   class Meta:
  #      model = Tag
  #      fields = [
   #         'list'
   #     ]
   #     labels = {
   #         'list': 'Listas'
   #     }
