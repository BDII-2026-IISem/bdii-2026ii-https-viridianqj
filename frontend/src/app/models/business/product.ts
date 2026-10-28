export interface ProductI {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  price: string;
  status: 'ACTIVE' | 'INACTIVE';
  createdAt: string;
  updatedAt: string;
}
