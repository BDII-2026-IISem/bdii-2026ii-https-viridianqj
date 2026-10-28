import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { environment } from '../../environments/environment';
import { DevAuth } from './dev-auth';

export const devAuthInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(DevAuth);

  // Solo se intercepta la API de BrasaGo, y nunca las rutas de /auth/.
  if (!req.url.startsWith(environment.apiUrl) || req.url.includes('/auth/')) {
    return next(req);
  }

  const withToken = (token: string) =>
    req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });

  return auth.getToken().pipe(
    switchMap((token) =>
      next(withToken(token)).pipe(
        catchError((err: HttpErrorResponse) => {
          if (err.status !== 401) {
            return throwError(() => err);
          }
          // El token venció: se pide uno nuevo y se repite la petición una vez.
          auth.clear();
          return auth.login().pipe(switchMap((t) => next(withToken(t))));
        }),
      ),
    ),
  );
};