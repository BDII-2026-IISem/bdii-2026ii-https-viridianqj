from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.security.models import Resource, ResourceRole, Role, RoleUser, User


class Command(BaseCommand):
    help = "Da a un usuario un rol con acceso a TODOS los recursos registrados (solo desarrollo)."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--role", default="ADMIN")

    def handle(self, *args, **options):
        user = User.objects.filter(username=options["username"]).first()
        if user is None:
            raise CommandError(f"No existe el usuario {options['username']!r}.")

        call_command("seed_rbac", stdout=self.stdout)  # asegura los recursos
        role, _ = Role.objects.get_or_create(name=options["role"])
        RoleUser.objects.get_or_create(role=role, user=user)
        granted = ResourceRole.objects.filter(role=role).values_list("resource_id", flat=True)
        missing = Resource.objects.exclude(id__in=granted)
        ResourceRole.objects.bulk_create([ResourceRole(resource=r, role=role) for r in missing])
        self.stdout.write(
            self.style.SUCCESS(
                f"{user.username} → rol {role.name}: {Resource.objects.count()} recursos concedidos."
            )
        )
