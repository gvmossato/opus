from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('app/', include('appsite.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('favicon.ico', RedirectView.as_view(url="static/images/favicon.png")), # Fix favicon
]
