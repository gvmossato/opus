from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse

from .forms import UserForm
from appsite.models import Profile
from django.views.decorators.csrf import csrf_protect

@login_required
def login_redirect(request):
    return redirect('appsite:profile_detail', pk=request.user.pk)

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.content_subtype = "html"
            email.send()
            return HttpResponseRedirect( reverse_lazy('login') )
    else:
        form = UserForm()
    return render(request, 'registration/index.html', {'form': form})


"""
class CreateUserView(generic.CreateView):
    form_class = UserForm
    template_name = 'registration/index.html'

    def form_valid(self, form):
        #If the form is valid, redirect to the supplied URL.
        self.form = form    
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.form.is_valid():
            user = self.form.save(commit=False)
            user.is_active = False
            user.save()
        #username = self.form.cleaned_data['username']
        #user = User.objects.get(username=username)
        #user.is_active = False
        #user.save()
            current_site = get_current_site(self.request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('accounts/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = user.email
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.content_subtype = "html"
            email.send()
            
            return reverse_lazy('login')

"""
   

@csrf_protect
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')