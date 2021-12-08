from django.conf import settings
from django.db import models


# Tabela auxiliar de usuários
# class UserData(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    picture = models.URLField(max_length=255, null=True)

# Tabela de usuários (nativa do Django)
# class Users(models.Model):
# ...

class List(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=2)
    description = models.CharField(max_length=255, null=True)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Job')

# # Tabela auxiliar de cargos
# class JobType(models.Model):
#     name = models.CharField(max_length=255)

# Tabela intermediária de Users e Lists (NxN)
class Job(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    active_invite = models.BooleanField()
    type = models.IntegerField()

class Task(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    origin = models.IntegerField()
    name = models.CharField(max_length=255)
    done = models.BooleanField(default=False)

class Tag(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL) # Tabela intermediária de Users e Tags (NxN)
