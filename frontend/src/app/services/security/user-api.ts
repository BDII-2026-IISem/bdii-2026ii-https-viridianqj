import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { UserI, UserPayload, UserPermission } from '../../models/security/user';
import { CrudApi } from './crud';

@Injectable({ providedIn: 'root' })
export class UserApi extends CrudApi<UserI, UserPayload> {
  protected readonly path = 'users';

  /** Permisos efectivos del usuario, para el diálogo "Ver permisos" (AC-10-04). */
  permissions(id: number): Observable<UserPermission[]> {
    return this.http
      .get<{ permissions: UserPermission[] }>(`${this.collection}${id}/permissions/`)
      .pipe(map((res) => res.permissions));
  }
}
