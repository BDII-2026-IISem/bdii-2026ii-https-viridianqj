from django.core.management.base import BaseCommand
from django.urls import URLResolver, get_resolver

from apps.security.models import HttpMethod, Resource
from apps.security.permissions import HasResourceAccess

SKIP_FRAGMENTS = ("schema", "admin/", "(?P<format>")
SKIP_NAMES = {"api-root"}


def join_route(route1, route2):
    """Misma regla que usa Django para armar ResolverMatch.route."""
    if not route1:
        return route2
    return route1 + route2.removeprefix("^")


def iter_routes(patterns, prefix=""):
    for pattern in patterns:
        route = join_route(prefix, str(pattern.pattern))
        if isinstance(pattern, URLResolver):
            yield from iter_routes(pattern.url_patterns, route)
        else:
            yield route, pattern


def governed_by_matrix(callback):
    """True solo si la vista pasa por HasResourceAccess (no es abierta ni solo-JWT)."""
    view_cls = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
    if view_cls is None:
        return False
    return any(
        isinstance(p, type) and issubclass(p, HasResourceAccess)
        for p in getattr(view_cls, "permission_classes", [])
    )


def methods_for(callback):
    actions = getattr(callback, "actions", None)  # ViewSet.as_view({...})
    if actions:
        names = actions.keys()
    else:
        view_class = getattr(callback, "view_class", None)
        if view_class is None:
            return []
        names = [
            m for m in view_class.http_method_names
            if m not in ("options", "head", "trace") and hasattr(view_class, m)
        ]
    return [m.upper() for m in names if m.upper() in HttpMethod.values]


class Command(BaseCommand):
    help = "Registra en `resources` cada método+ruta de la API (idempotente)."

    def handle(self, *args, **options):
        created = existing = 0
        for route, pattern in iter_routes(get_resolver().url_patterns):
            if not route.startswith("api/"):
                continue
            if any(fragment in route for fragment in SKIP_FRAGMENTS):
                continue
            if pattern.name in SKIP_NAMES:
                continue
            if not governed_by_matrix(pattern.callback):
                continue
            for method in methods_for(pattern.callback):
                _, was_created = Resource.objects.get_or_create(method=method, route=route)
                if was_created:
                    created += 1
                else:
                    existing += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"seed_rbac: {created} recursos nuevos, {existing} ya existían, "
                f"{Resource.objects.count()} en total."
            )
        )
