import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, finalize, map, shareReplay, switchMap, tap, throwError } from 'rxjs';

import { environment } from '../../environments/environment';
import { SessionStore, SessionUser, TokenPair } from '../core/session';

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
      switchMap(() => this.profile()),
      catchError((err) => {
        this.session.clear();
        return throwError(() => err);
      }),
    );
  }

  profile(): Observable<SessionUser> {
    return this.http
      .get<SessionUser>(`${this.base}/profile/`)
      .pipe(tap((user) => this.session.setUser(user)));
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
            this.router.navigate(['/login']);
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
