from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
        ]
        labels = {
            'username' : 'Usuário',
            'email'    : 'E-mail',
        }
