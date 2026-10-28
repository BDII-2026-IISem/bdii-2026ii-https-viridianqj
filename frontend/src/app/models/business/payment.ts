export interface PaymentI {
  id: number;
  order: number;
  method: string;
  amount: string;
  paidAt: string;
  paymentStatus: string;
  status: 'ACTIVE' | 'INACTIVE';
}
