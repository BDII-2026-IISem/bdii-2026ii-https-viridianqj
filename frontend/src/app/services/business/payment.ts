import { Injectable } from '@angular/core';

import { PaymentI } from '../../models/business/payment';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class PaymentService extends BaseApi<PaymentI> {
  protected readonly path = 'pagos';
}
