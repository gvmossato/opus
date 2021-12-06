from django.conf import settings
from django.db import models


# Tabela auxiliar de usuários
class UserData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False)
    picture = models.URLField(max_length=255, null=True)

# Tabela de usuários (nativa do Django)
# class Users(models.Model):
# ...

class Lists(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=2)
    description = models.CharField(max_length=255, null=True)
    deleted = models.BooleanField(default=False)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Jobs')

# Tabela auxiliar de cargos
class JobsType(models.Model):
    name = models.CharField(max_length=255)

# Tabela intermediária de Users e Lists (NxN)
class Jobs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    list = models.ForeignKey(Lists, on_delete=models.CASCADE)
    active_invite = models.BooleanField()
    type = models.ForeignKey(JobsType, on_delete=models.CASCADE)

class Tasks(models.Model):
    list = models.ForeignKey(Lists, on_delete=models.CASCADE)
    origin = models.IntegerField()
    name = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

class Tags(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL) # Tabela intermediária de Users e Tags (NxN)
