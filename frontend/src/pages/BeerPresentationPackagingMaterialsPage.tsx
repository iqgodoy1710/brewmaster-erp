import { useCallback, useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  BeerPresentationPackagingMaterial,
  RawMaterialReference,
  PackagingFormat,
  Category,
} from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

const formatQuantity = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

function BeerPresentationPackagingMaterialsPage() {
  const currentUser = useCurrentUser();

  const canManageCatalog =
    hasRole(currentUser, "admin") || hasRole(currentUser, "operator");
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [packagingFormats, setPackagingFormats] = useState<PackagingFormat[]>(
    [],
  );
  const [rawMaterials, setRawMaterials] = useState<RawMaterialReference[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [rawMaterialSearch, setRawMaterialSearch] = useState("");
  const [rawMaterialCategoryId, setRawMaterialCategoryId] = useState("");
  const [materials, setMaterials] = useState<
    BeerPresentationPackagingMaterial[]
  >([]);
  const [beerPresentationId, setBeerPresentationId] = useState("");
  const [rawMaterialId, setRawMaterialId] = useState("");
  const [requiredQuantity, setRequiredQuantity] = useState("1.000");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const selectedPresentation = useMemo(
    () =>
      presentations.find(
        (presentation) => presentation.id === Number(beerPresentationId),
      ) ?? null,
    [beerPresentationId, presentations],
  );

  const materialPresentations = useMemo(() => {
    const formatById = new Map(
      packagingFormats.map((format) => [format.id, format]),
    );

    return presentations.filter(
      (presentation) =>
        formatById.get(presentation.packaging_format_id)?.format_type !== "keg",
    );
  }, [packagingFormats, presentations]);

  const rawMaterialById = useMemo(
    () =>
      new Map(rawMaterials.map((rawMaterial) => [rawMaterial.id, rawMaterial])),
    [rawMaterials],
  );

  const filteredRawMaterials = useMemo(() => {
    const normalizedSearch = rawMaterialSearch.trim().toLowerCase();

    return rawMaterials.filter((rawMaterial) => {
      const matchesCategory =
        !rawMaterialCategoryId ||
        rawMaterial.category_id === Number(rawMaterialCategoryId);

      const matchesSearch =
        !normalizedSearch ||
        `${rawMaterial.code} ${rawMaterial.name}`
          .toLowerCase()
          .includes(normalizedSearch);

      return matchesCategory && matchesSearch;
    });
  }, [rawMaterialCategoryId, rawMaterialSearch, rawMaterials]);

  const loadBaseData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [presentationsData, rawMaterialsData, formatsData, categoriesData] =
        await Promise.all([
          apiGet<BeerPresentation[]>("/beer-presentations/"),
          apiGet<RawMaterialReference[]>("/raw-materials/references"),
          apiGet<PackagingFormat[]>("/packaging-formats/"),
          apiGet<Category[]>("/categories/"),
        ]);

      setPresentations(presentationsData);
      setPackagingFormats(formatsData);
      setRawMaterials(rawMaterialsData);
      setCategories(categoriesData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadMaterials = useCallback(async () => {
    if (!beerPresentationId) {
      setMaterials([]);
      return;
    }

    try {
      setError(null);

      const data = await apiGet<BeerPresentationPackagingMaterial[]>(
        `/beer-presentations/${beerPresentationId}/packaging-materials`,
      );

      setMaterials(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los materiales de envasado.",
      );
    }
  }, [beerPresentationId]);

  useEffect(() => {
    void loadBaseData();
  }, [loadBaseData]);

  useEffect(() => {
    void loadMaterials();
  }, [loadMaterials]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!beerPresentationId || !rawMaterialId) {
      setError("Seleccioná una presentación y un insumo.");
      return;
    }

    if (Number(requiredQuantity) <= 0) {
      setError("La cantidad requerida debe ser mayor que cero.");
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      await apiPost<BeerPresentationPackagingMaterial>(
        "/beer-presentation-packaging-materials/",
        {
          beer_presentation_id: Number(beerPresentationId),
          raw_material_id: Number(rawMaterialId),
          required_quantity: requiredQuantity,
        },
      );

      setRawMaterialId("");
      setRequiredQuantity("1.000");
      setSuccess("Material de envasado agregado correctamente.");

      await loadMaterials();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo agregar el material de envasado.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Envasado</p>
        <h1>Materiales de envasado</h1>
        <p>
          Configurá los insumos consumibles necesarios para producir botellas,
          latas u otras presentaciones no retornables.
        </p>
      </section>

      {isLoading && <p>Cargando datos...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {!isLoading && (
        <>
          {canManageCatalog ? (
            <section className="panel">
              <h2>Asignar material</h2>

              <form className="sale-form" onSubmit={handleSubmit}>
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
                    Categoría
                    <select
                      onChange={(event) =>
                        setRawMaterialCategoryId(event.target.value)
                      }
                      value={rawMaterialCategoryId}
                    >
                      <option value="">Todas las categorías</option>

                      {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="form-grid">
                  <label>
                    Presentación
                    <select
                      value={beerPresentationId}
                      onChange={(event) =>
                        setBeerPresentationId(event.target.value)
                      }
                    >
                      <option value="">Seleccioná una presentación</option>
                      {materialPresentations.map((presentation) => (
                        <option key={presentation.id} value={presentation.id}>
                          {presentation.code} · {presentation.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Insumo
                    <select
                      value={rawMaterialId}
                      onChange={(event) => setRawMaterialId(event.target.value)}
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
                    Cantidad requerida por unidad
                    <input
                      min="0.001"
                      step="0.001"
                      type="number"
                      value={requiredQuantity}
                      onChange={(event) =>
                        setRequiredQuantity(event.target.value)
                      }
                    />
                  </label>
                </div>

                <button disabled={isSaving} type="submit">
                  {isSaving ? "Agregando..." : "Agregar material"}
                </button>
              </form>
            </section>
          ) : (
            <section className="panel">
              <h2>Consultar materiales</h2>

              <label>
                Presentación
                <select
                  value={beerPresentationId}
                  onChange={(event) =>
                    setBeerPresentationId(event.target.value)
                  }
                >
                  <option value="">Seleccioná una presentación</option>
                  {presentations.map((presentation) => (
                    <option key={presentation.id} value={presentation.id}>
                      {presentation.code} · {presentation.name}
                    </option>
                  ))}
                </select>
              </label>
            </section>
          )}

          <section className="panel">
            <h2>
              {selectedPresentation
                ? `Materiales de ${selectedPresentation.name}`
                : "Materiales asignados"}
            </h2>

            {!selectedPresentation ? (
              <p className="empty-state">
                Seleccioná una presentación para consultar sus materiales.
              </p>
            ) : materials.length === 0 ? (
              <p className="empty-state">
                Esta presentación todavía no tiene materiales asignados.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Insumo</th>
                      <th>Código</th>
                      <th>Cantidad por unidad</th>
                    </tr>
                  </thead>
                  <tbody>
                    {materials.map((material) => {
                      const rawMaterial = rawMaterialById.get(
                        material.raw_material_id,
                      );

                      return (
                        <tr key={material.id}>
                          <td>{rawMaterial?.name ?? "Insumo no disponible"}</td>
                          <td>{rawMaterial?.code ?? "—"}</td>
                          <td>{formatQuantity(material.required_quantity)}</td>
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

export default BeerPresentationPackagingMaterialsPage;
