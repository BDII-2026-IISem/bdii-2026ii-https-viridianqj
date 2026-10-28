import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ProductI } from '../../models/business/product';
import { BaseApi } from '../api';

export interface ProductPayload {
  sku: string;
  name: string;
  description: string | null;
  price: string;
}

@Injectable({ providedIn: 'root' })
export class ProductService extends BaseApi<ProductI> {
  protected readonly path = 'productos';

  private get collection(): string {
    return `${environment.apiUrl}/${this.path}/`;
  }

  create(payload: ProductPayload): Observable<ProductI> {
    return this.http.post<ProductI>(this.collection, payload);
  }

  update(id: number, payload: Partial<ProductPayload>): Observable<ProductI> {
    return this.http.patch<ProductI>(`${this.collection}${id}/`, payload);
  }

  remove(id: number): Observable<void> {
    return this.http.delete<void>(`${this.collection}${id}/`);
  }
}
