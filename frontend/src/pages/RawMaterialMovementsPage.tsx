import { useCallback, useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  RawMaterial,
  RawMaterialMovementType,
  RawMaterialStockMovement,
  Supplier,
} from "../types/api";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

const formatCurrency = (value: string | null) =>
  value === null
    ? "—"
    : new Intl.NumberFormat("es-ES", {
        style: "currency",
        currency: "USD",
        currencyDisplay: "narrowSymbol",
      }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

const movementLabels: Record<RawMaterialMovementType, string> = {
  purchase_receipt: "Recepción de compra",
  production_consumption: "Consumo de producción",
  initial_balance: "Saldo inicial",
  waste: "Merma",
  expiration: "Vencimiento",
  inventory_adjustment_in: "Ajuste de entrada",
  inventory_adjustment_out: "Ajuste de salida",
};

const manualMovementTypes: RawMaterialMovementType[] = [
  "purchase_receipt",
  "initial_balance",
  "waste",
  "expiration",
  "inventory_adjustment_in",
  "inventory_adjustment_out",
];

function RawMaterialMovementsPage() {
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [movements, setMovements] = useState<RawMaterialStockMovement[]>([]);
  const [rawMaterialId, setRawMaterialId] = useState("");
  const [rawMaterialSearch, setRawMaterialSearch] = useState("");
  const [movementType, setMovementType] =
    useState<RawMaterialMovementType>("purchase_receipt");
  const [quantity, setQuantity] = useState("");
  const [supplierId, setSupplierId] = useState("");
  const [unitCost, setUnitCost] = useState("");
  const [reference, setReference] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadBaseData = useCallback(async () => {
    try {
      const [rawMaterialsData, suppliersData] = await Promise.all([
        apiGet<RawMaterial[]>("/raw-materials/"),
        apiGet<Supplier[]>("/suppliers/"),
      ]);

      setRawMaterials(rawMaterialsData);
      setSuppliers(suppliersData);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos de insumos.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadMovements = useCallback(async (materialId: string) => {
    if (!materialId) {
      setMovements([]);
      return;
    }

    setIsHistoryLoading(true);

    try {
      const data = await apiGet<RawMaterialStockMovement[]>(
        `/raw-material-stock-movements/${materialId}`,
      );
      setMovements(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cargar el historial de movimientos.",
      );
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBaseData();
  }, [loadBaseData]);

  useEffect(() => {
    loadMovements(rawMaterialId);
  }, [loadMovements, rawMaterialId]);

  const selectedRawMaterial = useMemo(
    () =>
      rawMaterials.find(
        (rawMaterial) => rawMaterial.id === Number(rawMaterialId),
      ),
    [rawMaterialId, rawMaterials],
  );
  const filteredRawMaterials = useMemo(() => {
    const normalizedSearch = rawMaterialSearch.trim().toLowerCase();

    if (!normalizedSearch) {
      return rawMaterials;
    }

    return rawMaterials.filter((rawMaterial) =>
      `${rawMaterial.code} ${rawMaterial.name}`
        .toLowerCase()
        .includes(normalizedSearch),
    );
  }, [rawMaterialSearch, rawMaterials]);

  const requiresSupplier = movementType === "purchase_receipt";

  async function createMovement(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const parsedQuantity = Number(quantity);
    const parsedUnitCost = Number(unitCost);

    if (!rawMaterialId) {
      setError("Seleccioná un insumo.");
      return;
    }

    if (!Number.isFinite(parsedQuantity) || parsedQuantity <= 0) {
      setError("La cantidad debe ser mayor a cero.");
      return;
    }

    if (requiresSupplier && !supplierId) {
      setError("Seleccioná un proveedor para la recepción de compra.");
      return;
    }

    if (
      requiresSupplier &&
      (!Number.isFinite(parsedUnitCost) || parsedUnitCost < 0)
    ) {
      setError("El costo unitario debe ser igual o mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    const movementData: Record<string, unknown> = {
      raw_material_id: Number(rawMaterialId),
      movement_type: movementType,
      quantity,
      reference: reference.trim() || null,
      notes: notes.trim() || null,
    };

    if (requiresSupplier) {
      movementData.supplier_id = Number(supplierId);
      movementData.unit_cost = unitCost;
    }

    try {
      const movement = await apiPost<RawMaterialStockMovement>(
        "/raw-material-stock-movements/",
        movementData,
      );

      setQuantity("");
      setSupplierId("");
      setUnitCost("");
      setReference("");
      setNotes("");
      setSuccess(
        `El movimiento ${movementLabels[movement.movement_type]} fue registrado.`,
      );

      await Promise.all([loadBaseData(), loadMovements(rawMaterialId)]);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar el movimiento.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Inventario</p>
        <h1>Movimientos de insumos</h1>
        <p>
          Registrá ingresos y ajustes, y consultá el historial de cada insumo.
        </p>
      </section>

      {isLoading && <p>Cargando movimientos de insumos...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {!isLoading && hasLoaded && (
        <>
          <section className="panel sales-form-panel">
            <h2>Registrar movimiento</h2>

            <form className="sale-form" onSubmit={createMovement}>
              <div className="form-grid">
                <label>
                  Buscar insumo
                  <input
                    onChange={(event) =>
                      setRawMaterialSearch(event.target.value)
                    }
                    placeholder="Código o nombre"
                    type="search"
                    value={rawMaterialSearch}
                  />
                </label>
                <label>
                  Insumo
                  <select
                    onChange={(event) => setRawMaterialId(event.target.value)}
                    required
                    value={rawMaterialId}
                  >
                    <option value="">Seleccioná un insumo</option>
                    {filteredRawMaterials.map((rawMaterial) => (
                      <option key={rawMaterial.id} value={rawMaterial.id}>
                        {rawMaterial.code} · {rawMaterial.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Tipo de movimiento
                  <select
                    onChange={(event) =>
                      setMovementType(
                        event.target.value as RawMaterialMovementType,
                      )
                    }
                    value={movementType}
                  >
                    {manualMovementTypes.map((type) => (
                      <option key={type} value={type}>
                        {movementLabels[type]}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="form-grid">
                <label>
                  Cantidad
                  <input
                    min="0.001"
                    onChange={(event) => setQuantity(event.target.value)}
                    required
                    step="0.001"
                    type="number"
                    value={quantity}
                  />
                </label>

                <label>
                  Referencia
                  <input
                    maxLength={100}
                    onChange={(event) => setReference(event.target.value)}
                    placeholder="PUR-001"
                    value={reference}
                  />
                </label>
              </div>

              {requiresSupplier && (
                <div className="form-grid">
                  <label>
                    Proveedor
                    <select
                      onChange={(event) => setSupplierId(event.target.value)}
                      required
                      value={supplierId}
                    >
                      <option value="">Seleccioná un proveedor</option>
                      {suppliers.map((supplier) => (
                        <option key={supplier.id} value={supplier.id}>
                          {supplier.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Costo unitario
                    <input
                      min="0"
                      onChange={(event) => setUnitCost(event.target.value)}
                      required
                      step="0.01"
                      type="number"
                      value={unitCost}
                    />
                  </label>
                </div>
              )}

              <label>
                Notas
                <input
                  onChange={(event) => setNotes(event.target.value)}
                  placeholder="Notas opcionales del movimiento."
                  value={notes}
                />
              </label>

              <button disabled={isSaving} type="submit">
                {isSaving ? "Registrando..." : "Registrar movimiento"}
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>Historial del insumo</h2>

            {selectedRawMaterial && (
              <p className="selected-material">
                <strong>{selectedRawMaterial.name}</strong>
                {" · Stock actual: "}
                {formatNumber(selectedRawMaterial.current_stock)}
              </p>
            )}

            {!selectedRawMaterial ? (
              <p className="empty-state">
                Seleccioná un insumo para ver su historial.
              </p>
            ) : isHistoryLoading ? (
              <p>Cargando historial...</p>
            ) : movements.length === 0 ? (
              <p className="empty-state">
                Todavía no hay movimientos para este insumo.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Tipo</th>
                      <th>Cantidad</th>
                      <th>Proveedor</th>
                      <th>Costo</th>
                      <th>Referencia</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movements.map((movement) => {
                      const supplier = suppliers.find(
                        (currentSupplier) =>
                          currentSupplier.id === movement.supplier_id,
                      );

                      return (
                        <tr key={movement.id}>
                          <td>{formatDate(movement.occurred_at)}</td>
                          <td>{movementLabels[movement.movement_type]}</td>
                          <td>{formatNumber(movement.quantity)}</td>
                          <td>{supplier?.name ?? "—"}</td>
                          <td>{formatCurrency(movement.unit_cost)}</td>
                          <td>{movement.reference ?? "—"}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}

export default RawMaterialMovementsPage;
