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

export type Category = {
  id: number;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type Unit = {
  id: number;
  name: string;
  symbol: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type SaleDetailItem = {
  beer_presentation_id: number;
  beer_presentation_code: string;
  beer_presentation_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
};

export type SaleDetail = {
  id: number;
  code: string;
  customer_id: number;
  customer_name: string;
  status: SaleStatus;
  notes: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  created_at: string;
  updated_at: string;
  items: SaleDetailItem[];
  total_amount: string;
};

export type UserRole = "admin" | "operator" | "management";

export type AuthenticatedUser = {
  id: number;
  username: string;
  full_name: string;
  role: UserRole;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type RawMaterialReference = {
  id: number;
  code: string;
  name: string;
  category_id: number;
  unit_symbol: string;
};

export type BeerPresentationPrice = {
  id: number;
  beer_presentation_id: number;
  unit_price: string;
  effective_from: string;
  notes: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type BeerPresentationCostComponent = {
  component_type: "beer" | "packaging";
  raw_material_id: number;
  raw_material_code: string;
  raw_material_name: string;
  unit_symbol: string;
  quantity: string;
  unit_cost: string;
  subtotal: string;
};

export type BeerPresentationCostEstimate = {
  beer_presentation_id: number;
  beer_presentation_code: string;
  beer_presentation_name: string;
  packaging_volume_liters: string;
  recipe_id: number;
  recipe_version: number;
  recipe_target_volume_liters: string;
  beer_cost: string;
  packaging_material_cost: string;
  total_unit_cost: string;
  components: BeerPresentationCostComponent[];
};

export type CustomerPaymentMethod = "cash" | "bank_transfer" | "card" | "other";

export type CustomerPayment = {
  id: number;
  code: string;
  customer_id: number;
  amount: string;
  payment_method: CustomerPaymentMethod;
  reference: string | null;
  notes: string | null;
  occurred_at: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type CustomerAccountMovementType =
  | "sale_charge"
  | "payment"
  | "sale_cancellation";

export type CustomerAccountMovement = {
  id: number;
  customer_id: number;
  sale_id: number | null;
  sale_code: string | null;
  payment_id: number | null;
  payment_code: string | null;
  movement_type: CustomerAccountMovementType;
  amount: string;
  reference: string | null;
  notes: string | null;
  occurred_at: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type CustomerAccount = {
  customer_id: number;
  customer_code: string;
  customer_name: string;
  balance: string;
  movements: CustomerAccountMovement[];
};

export type PackagingFormatType = "bottle" | "keg" | "can" | "other";

export type PackagingFormat = {
  id: number;
  code: string;
  name: string;
  capacity_liters: string;
  format_type: PackagingFormatType;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type KegFormFactor =
  | "standard"
  | "flat"
  | "slim";

export type KegStatus =
  | "clean_available"
  | "dirty"
  | "filled"
  | "at_customer"
  | "tapped"
  | "out_of_service";

export type Keg = {
  id: number;
  code: string;
  packaging_format_id: number;
  form_factor: KegFormFactor;
  status: KegStatus;
  current_volume_liters: string;
  beer_presentation_id: number | null;
  production_batch_id: number | null;
  customer_id: number | null;
  notes: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type KegMovementType =
  | "filling"
  | "delivery"
  | "return"
  | "washing"
  | "tapping"
  | "remnant_transfer"
  | "inventory_adjustment"
  | "out_of_service";

export type KegMovement = {
  id: number;
  keg_id: number;
  movement_type: KegMovementType;
  previous_status: KegStatus;
  new_status: KegStatus;
  resulting_volume_liters: string;
  beer_presentation_id: number | null;
  production_batch_id: number | null;
  packaging_run_id: number | null;
  sale_id: number | null;
  customer_id: number | null;
  reference: string | null;
  notes: string | null;
  occurred_at: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type KegRemnantTransferResponse = {
  production_batch_id: number;
  recovered_volume_liters: string;
  resulting_available_bulk_volume_liters: string;
  source_movements: KegMovement[];
};