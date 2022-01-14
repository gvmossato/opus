from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models

from .avatars.get_avataaars import generate_avatar


# Tabela complementar de usuários
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.URLField(
        default="",
        max_length=510,
        null=True
    )
    description = models.TextField(
        default="Adicione uma descrição pra completar seu perfil.",
        max_length=255,
        null=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.picture:
            self.picture = generate_avatar()
        super(Profile, self).save(*args,**kwargs)

@receiver(models.signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(models.signals.post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()
