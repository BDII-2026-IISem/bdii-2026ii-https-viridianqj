import { Injectable } from '@angular/core';

import { CourierI } from '../../models/business/courier';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class CourierService extends BaseApi<CourierI> {
  protected readonly path = 'domiciliarios';
}
