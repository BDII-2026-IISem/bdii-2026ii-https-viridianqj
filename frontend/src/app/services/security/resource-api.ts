import { Injectable } from '@angular/core';

import { ResourceI, ResourcePayload } from '../../models/security/resource';
import { CrudApi } from './crud';

@Injectable({ providedIn: 'root' })
export class ResourceApi extends CrudApi<ResourceI, ResourcePayload> {
  protected readonly path = 'resources';
}
