import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { environment } from '../../environments/environment';
import { AuthService } from '../services/auth';
import { SessionStore } from './session';

const PUBLIC_PATHS = ['/auth/login/', '/auth/refresh/', '/auth/logout/'];

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (!req.url.startsWith(environment.apiUrl) || PUBLIC_PATHS.some((p) => req.url.includes(p))) {
    return next(req);
  }

  const session = inject(SessionStore);
  const auth = inject(AuthService);
  const withToken = (token: string | null) =>
    token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

  return next(withToken(session.accessToken())).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status !== 401) {
        return throwError(() => err);
      }
      return auth.refreshAccess().pipe(switchMap((access) => next(withToken(access))));
    }),
  );
};
