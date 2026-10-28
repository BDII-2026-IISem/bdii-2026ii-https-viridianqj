import { Injectable } from '@angular/core';

import { OrderI } from '../../models/business/order';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class OrderService extends BaseApi<OrderI> {
  protected readonly path = 'pedidos';
}
