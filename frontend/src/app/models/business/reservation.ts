export interface ReservationI {
  id: number;
  client: number;
  clientName: string;
  table: number;
  tableName: string;
  startsAt: string;
  endsAt: string;
  reservationStatus: string;
  notes: string | null;
  status: 'ACTIVE' | 'INACTIVE';
}
