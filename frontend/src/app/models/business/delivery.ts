export interface DeliveryI {
  id: number;
  order: number;
  courier: number;
  courierName: string;
  startedAt: string | null;
  finishedAt: string | null;
  total: string;
  deliveryStatus: string;
  notes: string | null;
  status: 'ACTIVE' | 'INACTIVE';
}
