import { useCallback, useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  BeerPresentationPackagingMaterial,
  RawMaterialReference,
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
  const [rawMaterials, setRawMaterials] = useState<RawMaterialReference[]>([]);
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

  const rawMaterialById = useMemo(
    () =>
      new Map(rawMaterials.map((rawMaterial) => [rawMaterial.id, rawMaterial])),
    [rawMaterials],
  );

  const loadBaseData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [presentationsData, rawMaterialsData] = await Promise.all([
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<RawMaterialReference[]>("/raw-materials/references"),
      ]);

      setPresentations(presentationsData);
      setRawMaterials(rawMaterialsData);
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
        <p>Configurá los insumos necesarios para producir cada presentación.</p>
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

                  <label>
                    Insumo
                    <select
                      value={rawMaterialId}
                      onChange={(event) => setRawMaterialId(event.target.value)}
                    >
                      <option value="">Seleccioná un insumo</option>
                      {rawMaterials.map((rawMaterial) => (
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
