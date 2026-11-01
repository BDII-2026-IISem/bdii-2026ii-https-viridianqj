import { RecordStatus } from './status';

export interface RoleUserI {
  id: number;
  role: number;
  user: number;
  status: RecordStatus;
  createdAt: string;
  updatedAt: string;
}

export interface RoleUserPayload {
  role: number;
  user: number;
  status?: RecordStatus;
}
