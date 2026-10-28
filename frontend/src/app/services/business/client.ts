import { Injectable } from '@angular/core';

import { ClientI } from '../../models/business/client';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class ClientService extends BaseApi<ClientI> {
  protected readonly path = 'clientes';
}
