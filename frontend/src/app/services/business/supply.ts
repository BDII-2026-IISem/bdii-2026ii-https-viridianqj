import { Injectable } from '@angular/core';

import { SupplyI } from '../../models/business/supply';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class SupplyService extends BaseApi<SupplyI> {
  protected readonly path = 'insumos';
}
