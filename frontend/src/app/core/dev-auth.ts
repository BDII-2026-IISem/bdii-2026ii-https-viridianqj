import { HttpBackend, HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, finalize, map, of, shareReplay, tap } from 'rxjs';

import { devCredentials } from '../../environments/dev-credentials';
import { environment } from '../../environments/environment';

interface LoginResponse {
  access: string;
  refresh: string;
  tokenType: string;
  accessExpiresIn: number;
}

/** Acceso automático de DESARROLLO: inicia sesión solo y guarda el token en memoria. */
@Injectable({ providedIn: 'root' })
export class DevAuth {
  // HttpBackend salta los interceptores: así el login no se intercepta a sí mismo.
  private readonly http = new HttpClient(inject(HttpBackend));
  private token: string | null = null;
  private expiresAt = 0;
  private inflight$: Observable<string> | null = null;

  getToken(): Observable<string> {
    if (this.token && Date.now() < this.expiresAt) {
      return of(this.token);
    }
    return this.login();
  }

  login(): Observable<string> {
    if (!this.inflight$) {
      this.inflight$ = this.http
        .post<LoginResponse>(`${environment.apiUrl}/auth/login/`, devCredentials)
        .pipe(
          tap((r) => {
            this.token = r.access;
            this.expiresAt = Date.now() + (r.accessExpiresIn - 60) * 1000;
          }),
          map((r) => r.access),
          finalize(() => (this.inflight$ = null)),
          shareReplay(1),
        );
    }
    return this.inflight$;
  }

  clear(): void {
    this.token = null;
  }
}