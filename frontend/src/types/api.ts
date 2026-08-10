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

export type Customer = {
  id: number;
  code: string;
  name: string;
  tax_id: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  notes: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type SaleStatus = "draft" | "completed" | "cancelled";

export type Sale = {
  id: number;
  code: string;
  customer_id: number;
  notes: string | null;
  active: boolean;
  status: SaleStatus;
  completed_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type SaleItem = {
  id: number;
  sale_id: number;
  beer_presentation_id: number;
  quantity: number;
  unit_price: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type ProductionBatchStatus =
  | "planned"
  | "in_progress"
  | "completed"
  | "cancelled";

export type ProductionBatch = {
  id: number;
  code: string;
  recipe_id: number;
  planned_volume_liters: string;
  notes: string | null;
  active: boolean;
  status: ProductionBatchStatus;
  available_bulk_volume_liters: string;
  produced_volume_liters: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type RawMaterialPlanningProjection = {
  raw_material_id: number;
  raw_material_code: string;
  raw_material_name: string;
  unit_symbol: string;
  current_stock: string;
  planned_consumption: string;
  projected_available_stock: string;
  has_shortage: boolean;
};

export type Recipe = {
  id: number;
  beer_id: number;
  version: number;
  target_volume_liters: string;
  notes: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type PackagingRun = {
  id: number;
  code: string;
  production_batch_id: number;
  beer_presentation_id: number;
  packaged_quantity: number;
  notes: string | null;
  packaged_volume_liters: string;
  occurred_at: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type Supplier = {
  id: number;
  name: string;
  tax_id: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type RawMaterialMovementType =
  | "purchase_receipt"
  | "production_consumption"
  | "initial_balance"
  | "waste"
  | "expiration"
  | "inventory_adjustment_in"
  | "inventory_adjustment_out";

export type RawMaterialStockMovement = {
  id: number;
  raw_material_id: number;
  movement_type: RawMaterialMovementType;
  quantity: string;
  supplier_id: number | null;
  unit_cost: string | null;
  reference: string | null;
  notes: string | null;
  occurred_at: string;
  production_batch_id: number | null;
  packaging_run_id: number | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type Beer = {
  id: number;
  code: string;
  name: string;
  style: string | null;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type PackagingFormat = {
  id: number;
  code: string;
  name: string;
  capacity_liters: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type RecipeIngredient = {
  id: number;
  recipe_id: number;
  raw_material_id: number;
  required_quantity: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type BeerPresentationPackagingMaterial = {
  id: number;
  beer_presentation_id: number;
  raw_material_id: number;
  required_quantity: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};