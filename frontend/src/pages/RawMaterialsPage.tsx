import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiDelete, apiGet, apiPatch, apiPost } from "../lib/api";
import type { Category, RawMaterial, Unit } from "../types/api";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

const formatCurrency = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
    currencyDisplay: "narrowSymbol",
  }).format(Number(value));

function RawMaterialsPage() {
  const [editingRawMaterial, setEditingRawMaterial] =
    useState<RawMaterial | null>(null);
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [name, setName] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [unitId, setUnitId] = useState("");
  const [minimumStock, setMinimumStock] = useState("0.000");
  const [currentCost, setCurrentCost] = useState("0.00");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [rawMaterialsData, categoriesData, unitsData] = await Promise.all([
        apiGet<RawMaterial[]>("/raw-materials/"),
        apiGet<Category[]>("/categories/"),
        apiGet<Unit[]>("/units/"),
      ]);

      setRawMaterials(rawMaterialsData);
      setCategories(categoriesData);
      setUnits(unitsData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los insumos.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  function resetForm() {
    setEditingRawMaterial(null);

    setName("");
    setCategoryId("");
    setUnitId("");
    setMinimumStock("0.000");
    setCurrentCost("0.00");
    setDescription("");
  }

  function startEditing(rawMaterial: RawMaterial) {
    setEditingRawMaterial(rawMaterial);

    setName(rawMaterial.name);
    setCategoryId(String(rawMaterial.category_id));
    setUnitId(String(rawMaterial.unit_id));
    setMinimumStock(rawMaterial.minimum_stock);
    setCurrentCost(rawMaterial.current_cost);
    setDescription(rawMaterial.description ?? "");
    setError(null);
    setSuccess(null);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim() || !categoryId || !unitId) {
      setError("Completá nombre, categoría y unidad.");
      return;
    }

    if (Number(minimumStock) < 0 || Number(currentCost) < 0) {
      setError("El stock mínimo y el costo no pueden ser negativos.");
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      const payload = {
        name: name.trim(),
        category_id: Number(categoryId),
        unit_id: Number(unitId),
        minimum_stock: minimumStock,
        current_cost: currentCost,
        description: description.trim() || null,
      };

      if (editingRawMaterial) {
        await apiPatch<RawMaterial>(
          `/raw-materials/${encodeURIComponent(editingRawMaterial.code)}`,
          payload,
        );
        setSuccess("Insumo actualizado correctamente.");
      } else {
        const rawMaterial = await apiPost<RawMaterial>(
          "/raw-materials/",
          payload,
        );

        setSuccess(
          `El insumo ${rawMaterial.code} · ${rawMaterial.name} fue creado correctamente.`,
        );
      }

      resetForm();

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el insumo.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeactivate(rawMaterial: RawMaterial) {
    const confirmed = window.confirm(
      `¿Desactivar el insumo "${rawMaterial.name}"? ` +
        "Se conservará su historial de movimientos.",
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      await apiDelete<RawMaterial>(
        `/raw-materials/${encodeURIComponent(rawMaterial.code)}`,
      );

      if (editingRawMaterial?.id === rawMaterial.id) {
        resetForm();
      }

      setSuccess("Insumo desactivado correctamente.");
      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo desactivar el insumo.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Inventario</p>
        <h1>Insumos</h1>
        <p>Registrá insumos y consultá su stock, mínimo y costo actual.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      <section className="panel">
        <h2>{editingRawMaterial ? "Editar insumo" : "Nuevo insumo"}</h2>
        {!editingRawMaterial && (
          <p className="form-help">
            El código de insumo se asignará automáticamente al crearlo.
          </p>
        )}
        <form className="sale-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Nombre
              <input
                placeholder="Nombre del insumo"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>

            <label>
              Categoría
              <select
                value={categoryId}
                onChange={(event) => setCategoryId(event.target.value)}
              >
                <option value="">Seleccioná una categoría</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Unidad
              <select
                value={unitId}
                onChange={(event) => setUnitId(event.target.value)}
              >
                <option value="">Seleccioná una unidad</option>
                {units.map((unit) => (
                  <option key={unit.id} value={unit.id}>
                    {unit.name} · {unit.symbol}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Stock mínimo
              <input
                min="0"
                step="0.001"
                type="number"
                value={minimumStock}
                onChange={(event) => setMinimumStock(event.target.value)}
              />
            </label>

            <label>
              Costo unitario actual
              <input
                min="0"
                step="0.01"
                type="number"
                value={currentCost}
                onChange={(event) => setCurrentCost(event.target.value)}
              />
            </label>

            <label>
              Descripción
              <input
                placeholder="Descripción opcional"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />
            </label>
          </div>

          <div className="inline-actions">
            <button disabled={isSaving} type="submit">
              {isSaving
                ? "Guardando..."
                : editingRawMaterial
                  ? "Guardar cambios"
                  : "Crear insumo"}
            </button>

            {editingRawMaterial && (
              <button disabled={isSaving} onClick={resetForm} type="button">
                Cancelar edición
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="panel">
        <h2>Insumos registrados</h2>

        {isLoading ? (
          <p>Cargando insumos...</p>
        ) : rawMaterials.length === 0 ? (
          <p className="empty-state">Todavía no hay insumos registrados.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Insumo</th>
                  <th>Stock actual</th>
                  <th>Stock mínimo</th>
                  <th>Costo actual</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {rawMaterials.map((rawMaterial) => (
                  <tr key={rawMaterial.id}>
                    <td>{rawMaterial.code}</td>
                    <td>{rawMaterial.name}</td>
                    <td>{formatNumber(rawMaterial.current_stock)}</td>
                    <td>{formatNumber(rawMaterial.minimum_stock)}</td>
                    <td>{formatCurrency(rawMaterial.current_cost)}</td>
                    <td>
                      <div className="inline-actions">
                        <button
                          disabled={isSaving}
                          onClick={() => startEditing(rawMaterial)}
                          type="button"
                        >
                          Editar
                        </button>

                        <button
                          disabled={isSaving}
                          onClick={() => void handleDeactivate(rawMaterial)}
                          type="button"
                        >
                          Desactivar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default RawMaterialsPage;
