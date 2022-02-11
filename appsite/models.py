from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
    





class List(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=2)
    description = models.TextField(max_length=255, null=True)
    user = models.ManyToManyField(User, through='Job')
    date = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=7, default="#F20574")
    picture = models.URLField(
        max_length=510,
        default="https://images.unsplash.com/photo-1515847049296-a281d6401047?w=1920"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper()
        super(List,self).save(*args,**kwargs)


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
    creation_date = models.DateTimeField(auto_now_add=True)
    due_date = models.CharField(max_length=10)

    def __str__(self):
        return self.name

@receiver(models.signals.post_save, sender=Task)
def set_original_id(sender, instance, created, **kwargs):
    if created and not instance.original_id:
        instance.original_id = instance.id
        instance.save()


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


