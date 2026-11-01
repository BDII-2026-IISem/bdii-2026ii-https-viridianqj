import { RecordStatus } from './status';

export interface UserI {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  status: RecordStatus;
}

/** La contraseña solo viaja en el alta; en edición no se envía. */
export interface UserPayload {
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
  password?: string;
  status?: RecordStatus;
}

export interface UserPermission {
  method: string;
  path: string;
  role: string;
}
