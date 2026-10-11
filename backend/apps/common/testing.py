"""Ayudas para los tests de autenticación."""
from apps.security.models import User

PASSWORD = "Clave-123456"


def create_active_user(username="ana", email="ana@example.com", **extra):
    return User.objects.create_user(
        username=username, email=email, password=PASSWORD, **extra
    )


from rest_framework_simplejwt.tokens import AccessToken  # noqa: E402

from apps.security.models import Resource, ResourceRole, Role, RoleUser  # noqa: E402


def authenticate(client, user):
    """Envía un access token válido del usuario, sin pasar por el login."""
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")


def grant_access(user, method, route, role_name="TESTER"):
    """Crea (o reutiliza) la cadena completa usuario→rol→recurso, todo ACTIVE."""
    role, _ = Role.objects.get_or_create(name=role_name)
    RoleUser.objects.get_or_create(role=role, user=user)
    resource, _ = Resource.objects.get_or_create(method=method, route=route)
    link, _ = ResourceRole.objects.get_or_create(resource=resource, role=role)
    return {"role": role, "role_user": RoleUser.objects.get(role=role, user=user),
            "resource": resource, "resource_role": link}


from io import StringIO  # noqa: E402

from django.core.management import call_command  # noqa: E402
from django.urls import resolve  # noqa: E402


def grant(user, method, path, role_name=None):
    """Concede method+path (la ruta se toma de resolve(path).route), todo ACTIVE."""
    role, _ = Role.objects.get_or_create(name=role_name or f"test-role-{user.pk}")
    RoleUser.objects.get_or_create(role=role, user=user)
    resource, _ = Resource.objects.get_or_create(method=method, route=resolve(path).route)
    ResourceRole.objects.get_or_create(resource=resource, role=role)
    return role, resource


def grant_crud(user, collection, detail):
    """GET y POST en la colección; GET, PUT, PATCH y DELETE en el detalle."""
    for method in ("GET", "POST"):
        grant(user, method, collection)
    for method in ("GET", "PUT", "PATCH", "DELETE"):
        grant(user, method, detail)


def authenticate_as_admin(client):
    """Usuario 'api-admin' con un rol que concede TODOS los recursos de la API."""
    from apps.security.models import User

    user, _ = User.objects.get_or_create(
        username="api-admin", defaults={"email": "api-admin@example.com"}
    )
    call_command("seed_rbac", verbosity=0, stdout=StringIO())
    role, _ = Role.objects.get_or_create(name="API_ADMIN")
    RoleUser.objects.get_or_create(role=role, user=user)
    granted = ResourceRole.objects.filter(role=role).values_list("resource_id", flat=True)
    ResourceRole.objects.bulk_create(
        [ResourceRole(resource=r, role=role) for r in Resource.objects.exclude(id__in=granted)]
    )
    client.force_authenticate(user=user)
    return user
