import { Injectable } from '@angular/core';

import { RoleUserI, RoleUserPayload } from '../../models/security/role-user';
import { CrudApi } from './crud';

@Injectable({ providedIn: 'root' })
export class RoleUserApi extends CrudApi<RoleUserI, RoleUserPayload> {
  protected readonly path = 'role-users';
}
