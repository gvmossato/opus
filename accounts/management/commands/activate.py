from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Activate an User, so it can log-in.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Indicates the username of the user')
    
    def handle(self, *args, **kwargs):
        username = kwargs['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User "%s" does not exist' % username)
        
        if (user.is_active):
            self.stdout.write(self.style.SUCCESS('User "%s" is already activated' % username))
        else:
            user.is_active = True
            user.save()

            self.stdout.write(self.style.SUCCESS('Successfully activated user "%s"' % username))
       