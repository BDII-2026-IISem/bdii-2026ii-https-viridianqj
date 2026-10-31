import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from '../../services/auth';
import { SessionStore } from '../session';

// Solo para /login: si ya hay sesión, va al panel.
export const guestGuard: CanActivateFn = (): boolean | UrlTree => {
  const session = inject(SessionStore);
  const router = inject(Router);
  return session.isAuthenticated() ? router.createUrlTree(['/dashboard']) : true;
};

// Rutas que requieren sesión; si no la hay, va a /login conservando returnUrl.
export const authGuard: CanActivateFn = (_route, state) => {
  const session = inject(SessionStore);
  const router = inject(Router);
  return session.isAuthenticated()
    ? true
    : router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};

// Rutas con data.permission (formato "MÉTODO /api/recurso"). Carga permisos si aún no están.
export const permissionGuard: CanActivateFn = (route, state) => {
  const session = inject(SessionStore);
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!session.isAuthenticated()) {
    return router.createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
  }

  const key = route.data['permission'] as string | undefined;
  const decide = (): boolean | UrlTree =>
    !key || session.canPermission(key)
      ? true
      : router.createUrlTree(['/forbidden'], { queryParams: { permission: key } });

  if (session.permissions().length > 0) {
    return decide();
  }
  return auth.refreshSession().pipe(
    map(() => decide()),
    catchError(() => of(router.createUrlTree(['/login']))),
  );
};
