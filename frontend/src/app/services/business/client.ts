import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ClientI } from '../../models/business/client';
import { BaseApi } from '../api';

export interface ClientPayload {
  documentType: string;
  documentNumber: string;
  name: string;
  phone: string | null;
  email: string | null;
}

@Injectable({ providedIn: 'root' })
export class ClientService extends BaseApi<ClientI> {
  protected readonly path = 'clientes';

  private get collection(): string {
    return `${environment.apiUrl}/${this.path}/`;
  }

  create(payload: ClientPayload): Observable<ClientI> {
    return this.http.post<ClientI>(this.collection, payload);
  }

  update(id: number, payload: Partial<ClientPayload>): Observable<ClientI> {
    return this.http.patch<ClientI>(`${this.collection}${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.collection}${id}/`);
  }
}
