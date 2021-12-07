from django.urls import reverse_lazy

from .forms import UserForm
from django.views import generic

class CreateUserView(generic.CreateView):
    form_class = UserForm
    template_name = 'registration/index.html'

    def get_success_url(self):
        return reverse_lazy('appsite:detail', args=(self.object.id, ))

    #success_message = "Your profile was created successfully"
