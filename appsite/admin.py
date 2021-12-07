from django.contrib import admin

from .models import *

admin.site.register(UserData)
admin.site.register(Lists)
admin.site.register(JobsType)
admin.site.register(Jobs)
admin.site.register(Tasks)
admin.site.register(Tags)
