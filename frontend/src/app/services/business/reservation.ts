import { Injectable } from '@angular/core';

import { ReservationI } from '../../models/business/reservation';
import { BaseApi } from '../api';

@Injectable({ providedIn: 'root' })
export class ReservationService extends BaseApi<ReservationI> {
  protected readonly path = 'reservas';
}
