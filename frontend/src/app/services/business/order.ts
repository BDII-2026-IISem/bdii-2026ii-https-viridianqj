import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { OrderI } from '../../models/business/order';
import { BaseApi } from '../api';

export interface OrderPayload {
  clientId: number | null;
  branchId: number;
  tableId: number | null;
  channel: string;
  items: { productId: number; quantity: number }[];
}

@Injectable({ providedIn: 'root' })
export class OrderService extends BaseApi<OrderI> {
  protected readonly path = 'pedidos';

  private get collection(): string {
    return `${environment.apiUrl}/${this.path}/`;
  }

  create(payload: OrderPayload): Observable<OrderI> {
    return this.http.post<OrderI>(this.collection, payload);
  }

  getById(id: number): Observable<OrderI> {
    return this.http.get<OrderI>(`${this.collection}${id}/`);
  }

  void(id: number): Observable<void> {
    return this.http.delete<void>(`${this.collection}${id}/`);
  }
}
