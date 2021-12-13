from rest_framework.views import exception_handler
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response.status_code == 401:            
        return HttpResponseRedirect(reverse_lazy('accounts:redirect'))

    return response