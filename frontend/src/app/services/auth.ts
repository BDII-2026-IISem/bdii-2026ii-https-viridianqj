import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import {
  Observable,
  catchError,
  finalize,
  forkJoin,
  map,
  shareReplay,
  switchMap,
  tap,
  throwError,
} from 'rxjs';

import { environment } from '../../environments/environment';
import { EffectivePermission, SessionStore, SessionUser, TokenPair } from '../core/session';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly session = inject(SessionStore);
  private readonly router = inject(Router);
  private readonly base = `${environment.apiUrl}/auth`;

  // Refresh compartido: si varias peticiones reciben 401 a la vez, solo se pide un refresh.
  private inFlight: Observable<string> | null = null;

  login(username: string, password: string): Observable<SessionUser> {
    return this.http.post<TokenPair>(`${this.base}/login/`, { username, password }).pipe(
      tap((pair) => this.session.saveTokens(pair)),
      switchMap(() => this.refreshSession()),
      catchError((err) => {
        this.session.clear();
        return throwError(() => err);
      }),
    );
  }

  // Perfil y permisos en paralelo: la sesión queda lista solo cuando ambos responden.
  refreshSession(): Observable<SessionUser> {
    return forkJoin([this.profile(), this.permissions()]).pipe(map(([user]) => user));
  }

  profile(): Observable<SessionUser> {
    return this.http
      .get<SessionUser>(`${this.base}/profile/`)
      .pipe(tap((user) => this.session.setUser(user)));
  }

  permissions(): Observable<EffectivePermission[]> {
    return this.http
      .get<{ permissions: EffectivePermission[] }>(`${this.base}/permissions/`)
      .pipe(
        map((res) => res.permissions),
        tap((list) => this.session.setPermissions(list)),
      );
  }

  refreshAccess(): Observable<string> {
    if (!this.inFlight) {
      this.inFlight = this.http
        .post<TokenPair>(`${this.base}/refresh/`, { refresh: this.session.refreshToken() })
        .pipe(
          tap((pair) => this.session.saveTokens(pair)),
          map((pair) => pair.access),
          catchError((err) => {
            this.session.clear();
            this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
            return throwError(() => err);
          }),
          finalize(() => (this.inFlight = null)),
          shareReplay(1),
        );
    }
    return this.inFlight;
  }

  logout(): Observable<void> {
    return this.http
      .post<void>(`${this.base}/logout/`, { refresh: this.session.refreshToken() })
      .pipe(finalize(() => this.session.clear()));
  }
}
