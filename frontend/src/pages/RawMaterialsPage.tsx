import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Category, RawMaterial, Unit } from "../types/api";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }).format(Number(value));

const formatCurrency = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value));

function RawMaterialsPage() {
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [code, setCode] = useState("");
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

      const [rawMaterialsData, categoriesData, unitsData] =
        await Promise.all([
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

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!code.trim() || !name.trim() || !categoryId || !unitId) {
      setError("Completá código, nombre, categoría y unidad.");
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

      await apiPost<RawMaterial>("/raw-materials/", {
        code: code.trim(),
        name: name.trim(),
        category_id: Number(categoryId),
        unit_id: Number(unitId),
        minimum_stock: minimumStock,
        current_cost: currentCost,
        description: description.trim() || null,
      });

      setCode("");
      setName("");
      setCategoryId("");
      setUnitId("");
      setMinimumStock("0.000");
      setCurrentCost("0.00");
      setDescription("");
      setSuccess("Insumo creado correctamente.");

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
        <h2>Nuevo insumo</h2>

        <form className="sale-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Código
              <input
                placeholder="Ej.: LUP-CAS-001"
                value={code}
                onChange={(event) => setCode(event.target.value)}
              />
            </label>

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

          <button disabled={isSaving} type="submit">
            {isSaving ? "Creando..." : "Crear insumo"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>Insumos registrados</h2>

        {isLoading ? (
          <p>Cargando insumos...</p>
        ) : rawMaterials.length === 0 ? (
          <p className="empty-state">
            Todavía no hay insumos registrados.
          </p>
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