import { Injectable } from '@angular/core';

import { DeliveryI } from '../../models/business/delivery';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class DeliveryService extends BaseApi<DeliveryI> {
  protected readonly path = 'entregas';
}
