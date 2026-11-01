import { Injectable } from '@angular/core';

import { ResourceRoleI, ResourceRolePayload } from '../../models/security/resource-role';
import { CrudApi } from './crud';

@Injectable({ providedIn: 'root' })
export class ResourceRoleApi extends CrudApi<ResourceRoleI, ResourceRolePayload> {
  protected readonly path = 'resource-roles';
}
