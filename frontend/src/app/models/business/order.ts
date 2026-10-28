export interface OrderDetailI {
  id: number;
  product: number;
  productName: string;
  quantity: number;
  unitPrice: string;
  total: string;
  notes: string | null;
  status: 'ACTIVE' | 'INACTIVE';
}

export interface OrderI {
  id: number;
  client: number | null;
  clientName: string | null;
  branch: number;
  branchName: string;
  table: number | null;
  tableName: string | null;
  channel: 'MESA' | 'RECOGIDA' | 'DOMICILIO';
  orderedAt: string;
  subtotal: string;
  total: string;
  orderStatus: string;
  status: 'ACTIVE' | 'INACTIVE';
  details: OrderDetailI[];
  createdAt: string;
  updatedAt: string;
}
