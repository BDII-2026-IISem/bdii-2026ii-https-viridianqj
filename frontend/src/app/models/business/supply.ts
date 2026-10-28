export interface SupplyI {
  id: number;
  code: string;
  name: string;
  unit: string;
  minStock: string;
  status: 'ACTIVE' | 'INACTIVE';
}
