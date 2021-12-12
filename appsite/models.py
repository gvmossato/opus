from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models


# Tabela auxiliar de usuários
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.URLField(
        default="https://avataaars.io/?avatarStyle=Transparent&topType=LongHairStraight&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light",
        max_length=255,
        null=True
    )
    description = models.TextField(
        default="Adicione uma descrição pra completar seu perfil.",
        max_length=255,
        null=True
    )
    date = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()


# Tabela de usuários (nativa do Django)
# class Users(models.Model):
# ...


class List(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=2)
    picture = models.URLField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    user = models.ManyToManyField(User, through='Job')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Tabela intermediária de Users e Lists (NxN)
class Job(models.Model):
    job_choices = [(1, 'Convidado'), (2, 'Seguidor'), (3, 'Administrador'), (4, 'Criador')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    active_invite = models.BooleanField()
    type = models.IntegerField(choices=job_choices)


class Task(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    # original_id is set to null so we can assign the original_id = id
    # when creating the task
    original_id = models.IntegerField(blank=True, null=True) 
    name = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    task = models.ManyToManyField(Task)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    list = models.ManyToManyField(List, through='Follow')

    def __str__(self):
        return self.name


# Tabela intermediária de Users e Tags (NxN)
class Follow(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    source_id = models.IntegerField()
