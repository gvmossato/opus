from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from .forms import UserForm
from appsite.models import Profile


@login_required
def login_redirect(request):
    return redirect('appsite:detail', pk=request.user.pk)

class CreateUserView(generic.CreateView):
    form_class = UserForm
    template_name = 'registration/index.html'

    def get_success_url(self):
        return reverse_lazy('login')
