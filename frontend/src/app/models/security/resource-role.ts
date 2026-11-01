import { RecordStatus } from './status';

export interface ResourceRoleI {
  id: number;
  resource: number;
  role: number;
  status: RecordStatus;
  createdAt: string;
  updatedAt: string;
}

export interface ResourceRolePayload {
  resource: number;
  role: number;
  status?: RecordStatus;
}
