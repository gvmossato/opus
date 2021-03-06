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
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


from .forms import UserForm
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
            mail_subject = 'Activate your Opus account.'
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
   

@csrf_protect
def activate(request, uidb64, token):
    try:
        uid = force_text( urlsafe_base64_decode(uidb64) )
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponseRedirect( reverse_lazy('appsite:profile_detail', args=(user.id, ) ) )
    else:
        return HttpResponse('Activation link is invalid!')

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')