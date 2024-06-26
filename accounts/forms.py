from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


# Transforma labels em placeholders
class PlaceholderMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_names = list(self.fields.keys())
        for field_name in field_names:
            field = self.fields.get(field_name)
            field.widget.attrs.update({'placeholder' : field.label})


class UserForm(PlaceholderMixin, UserCreationForm):
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


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.widgets.TextInput(attrs={'placeholder' : 'Usuário'})
    )
    password = forms.CharField(
        widget=forms.widgets.PasswordInput(attrs={'placeholder' : 'Senha'})
    )


class ProfileForm(forms.ModelForm):
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
