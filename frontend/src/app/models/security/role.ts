import { RecordStatus } from './status';

export interface RoleI {
  id: number;
  name: string;
  status: RecordStatus;
  createdAt: string;
  updatedAt: string;
}

export interface RolePayload {
  name: string;
  status?: RecordStatus;
}
