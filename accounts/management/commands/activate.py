from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Activate an User, so it can log-in"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Indicates the username of the user")

    def handle(self, *args, **kwargs):
        username = kwargs["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")

        if (user.is_active):
            self.stdout.write(self.style.SUCCESS(f"User '{username}' is already activated"))
        else:
            user.is_active = True
            user.save()

            self.stdout.write(self.style.SUCCESS(f"Successfully activated user '{username}'"))
