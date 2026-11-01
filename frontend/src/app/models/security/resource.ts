import { RecordStatus } from './status';

export type HttpVerb = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface ResourceI {
  id: number;
  method: HttpVerb;
  route: string;
  status: RecordStatus;
  createdAt: string;
  updatedAt: string;
}

export interface ResourcePayload {
  method: HttpVerb;
  route: string;
  status?: RecordStatus;
}
