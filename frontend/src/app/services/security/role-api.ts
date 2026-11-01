import { Injectable } from '@angular/core';

import { RoleI, RolePayload } from '../../models/security/role';
import { CrudApi } from './crud';

@Injectable({ providedIn: 'root' })
export class RoleApi extends CrudApi<RoleI, RolePayload> {
  protected readonly path = 'roles';
}
