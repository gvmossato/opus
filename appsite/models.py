from django.contrib.auth.models import User
from django.db import models


# Tabela auxiliar de usuários
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.URLField(max_length=255, null=True)

# Tabela de usuários (nativa do Django)
# class Users(models.Model):
# ...

class List(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=2)
    description = models.CharField(max_length=255, null=True)
    user = models.ManyToManyField(User, through='Job')

# Tabela auxiliar de cargos
# class JobType(models.Model):
#     name = models.CharField(max_length=255)

# Tabela intermediária de Users e Lists (NxN)
class Job(models.Model):
    job_choices = [(1, 'Guest'), (2, 'Follower'), (3, 'Admin'), (4, 'Creator')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    active_invite = models.BooleanField()
    type = models.IntegerField(choices=job_choices)

class Task(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    origin = models.IntegerField()
    name = models.CharField(max_length=255)
    done = models.BooleanField(default=False)

class Tag(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    user = models.ManyToManyField(User) # Tabela intermediária de Users e Tags (NxN)
