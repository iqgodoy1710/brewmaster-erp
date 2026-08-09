export type RawMaterialLowStock = {
  raw_material_id: number;
  raw_material_code: string;
  raw_material_name: string;
  unit_symbol: string;
  current_stock: string;
  minimum_stock: string;
  shortage_quantity: string;
};

export type BeerPresentationLowStock = {
  beer_presentation_id: number;
  beer_presentation_code: string;
  beer_presentation_name: string;
  current_stock: number;
  minimum_stock: number;
  shortage_quantity: number;
};

export type CompletedSaleReportItem = {
  sale_id: number;
  sale_code: string;
  customer_id: number;
  customer_name: string;
  completed_at: string;
  total_units: number;
  total_amount: string;
};

export type RawMaterial = {
  id: number;
  code: string;
  name: string;
  category_id: number;
  unit_id: number;
  current_stock: string;
  minimum_stock: string;
  current_cost: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type BeerPresentation = {
  id: number;
  code: string;
  name: string;
  beer_id: number;
  packaging_format_id: number;
  minimum_stock: number;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
  current_stock: number;
};