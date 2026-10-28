export interface RecipeI {
  id: number;
  product: number;
  productName: string;
  supply: number;
  supplyName: string;
  quantity: string;
  status: 'ACTIVE' | 'INACTIVE';
}
