import { HttpClient } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { environment } from '../../environments/environment';

/** Respuesta paginada de DRF (por si se activa la paginación en el backend). */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** Cada entidad solo declara su ruta (`path`); aquí vive el GET común. */
export abstract class BaseApi<T> {
  protected readonly http = inject(HttpClient);
  protected abstract readonly path: string;

  getAll(): Observable<T[]> {
    return this.http
      .get<T[] | PaginatedResponse<T>>(`${environment.apiUrl}/${this.path}/`)
      .pipe(map((res) => (Array.isArray(res) ? res : res.results)));
  }
}