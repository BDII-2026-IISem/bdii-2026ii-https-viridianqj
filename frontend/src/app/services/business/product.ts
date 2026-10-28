import { Injectable } from '@angular/core';

import { ProductI } from '../../models/business/product';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class ProductService extends BaseApi<ProductI> {
  protected readonly path = 'productos';
}
