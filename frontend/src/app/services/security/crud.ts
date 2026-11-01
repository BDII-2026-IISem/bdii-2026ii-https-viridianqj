import { HttpClient } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../api';

/** CRUD común para las entidades de seguridad. Cada servicio solo declara su ruta. */
export abstract class CrudApi<T, P> {
  protected readonly http = inject(HttpClient);
  protected abstract readonly path: string;

  protected get collection(): string {
    return `${environment.apiUrl}/${this.path}/`;
  }

  getAll(): Observable<T[]> {
    return this.http
      .get<T[] | PaginatedResponse<T>>(this.collection)
      .pipe(map((res) => (Array.isArray(res) ? res : res.results)));
  }

  getById(id: number): Observable<T> {
    return this.http.get<T>(`${this.collection}${id}/`);
  }

  create(payload: P): Observable<T> {
    return this.http.post<T>(this.collection, payload);
  }

  update(id: number, payload: Partial<P>): Observable<T> {
    return this.http.patch<T>(`${this.collection}${id}/`, payload);
  }

  /** Baja lógica: el backend responde 204 y deja la fila en INACTIVE. */
  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.collection}${id}/`);
  }
}
