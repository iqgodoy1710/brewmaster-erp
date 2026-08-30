import { useEffect, useMemo, useState, useCallback } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  Beer,
  ProductionBatch,
  RawMaterialPlanningProjection,
  Recipe,
} from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

const statusLabels: Record<ProductionBatch["status"], string> = {
  planned: "Planificado",
  in_progress: "En proceso",
  completed: "Completado",
  cancelled: "Cancelado",
};

function ProductionPage() {
  const currentUser = useCurrentUser();

  const canManageOperations = hasRole(currentUser, "admin", "operator");

  const [batches, setBatches] = useState<ProductionBatch[]>([]);
  const [projections, setProjections] = useState<
    RawMaterialPlanningProjection[]
  >([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [beers, setBeers] = useState<Beer[]>([]);
  const [batchCode, setBatchCode] = useState("");
  const [recipeId, setRecipeId] = useState("");
  const [plannedVolume, setPlannedVolume] = useState("");
  const [notes, setNotes] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [completionVolumes, setCompletionVolumes] = useState<
    Record<number, string>
  >({});
  const [completingBatchId, setCompletingBatchId] = useState<number | null>(
    null,
  );
  const [success, setSuccess] = useState<string | null>(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProductionData = useCallback(async () => {
    try {
      const [batchesData, projectionsData, recipesData, beersData] =
        await Promise.all([
          apiGet<ProductionBatch[]>("/production-batches/"),
          apiGet<RawMaterialPlanningProjection[]>(
            "/production-batches/planning/raw-material-requirements",
          ),
          apiGet<Recipe[]>("/recipes/"),
          apiGet<Beer[]>("/beers/"),
        ]);

      setBatches(batchesData);
      setProjections(projectionsData);
      setRecipes(recipesData);
      setBeers(beersData);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos de producción.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProductionData();
  }, [loadProductionData]);

  async function createProductionBatch(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const volume = Number(plannedVolume);

    if (!batchCode.trim()) {
      setError("Ingresá un código para el lote.");
      return;
    }

    if (!recipeId) {
      setError("Seleccioná una receta.");
      return;
    }

    if (!Number.isFinite(volume) || volume <= 0) {
      setError("El volumen planificado debe ser mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const batch = await apiPost<ProductionBatch>("/production-batches/", {
        code: batchCode.trim(),
        recipe_id: Number(recipeId),
        planned_volume_liters: plannedVolume,
        notes: notes.trim() || null,
      });

      setBatchCode("");
      setRecipeId("");
      setPlannedVolume("");
      setNotes("");
      setSuccess(`El lote ${batch.code} fue creado correctamente.`);

      await loadProductionData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el lote de producción.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function completeProductionBatch(
    event: React.FormEvent<HTMLFormElement>,
    batch: ProductionBatch,
  ) {
    event.preventDefault();

    const producedVolume = Number(
      completionVolumes[batch.id] ?? batch.planned_volume_liters,
    );

    if (!Number.isFinite(producedVolume) || producedVolume <= 0) {
      setError("El volumen producido debe ser mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setCompletingBatchId(batch.id);

    try {
      const completedBatch = await apiPost<ProductionBatch>(
        `/production-batches/${encodeURIComponent(batch.code)}/complete`,
        {
          produced_volume_liters: String(producedVolume),
        },
      );

      setSuccess(
        `El lote ${completedBatch.code} fue completado correctamente.`,
      );

      await loadProductionData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo completar el lote de producción.",
      );
    } finally {
      setCompletingBatchId(null);
    }
  }

  const plannedBatches = useMemo(
    () => batches.filter((batch) => batch.status === "planned").length,
    [batches],
  );

  const availableBulkVolume = useMemo(
    () =>
      batches.reduce(
        (total, batch) => total + Number(batch.available_bulk_volume_liters),
        0,
      ),
    [batches],
  );

  const shortages = useMemo(
    () => projections.filter((projection) => projection.has_shortage).length,
    [projections],
  );
  const recipeLabel = (recipe: Recipe) => {
    const beerName =
      beers.find((beer) => beer.id === recipe.beer_id)?.name ??
      `Cerveza #${recipe.beer_id}`;

    return (
      `${beerName} · Versión ${recipe.version} · ` +
      `${formatNumber(recipe.target_volume_liters)} L`
    );
  };
  const batchStyle = (batch: ProductionBatch) => {
    const recipe = recipes.find(
      (currentRecipe) => currentRecipe.id === batch.recipe_id,
    );

    const beer = beers.find(
      (currentBeer) => currentBeer.id === recipe?.beer_id,
    );

    return beer?.style ?? "—";
  };

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Operación</p>
        <h1>Producción</h1>
        <p>Consultá los lotes y el consumo proyectado de materias primas.</p>
      </section>

      {isLoading && <p>Cargando datos de producción...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      {success && <p className="success-message">{success}</p>}

      {!isLoading && hasLoaded && (
        <>
          {canManageOperations ? (
            <section className="panel sales-form-panel">
              <h2>Planificar lote</h2>

              <form className="sale-form" onSubmit={createProductionBatch}>
                <div className="form-grid">
                  <label>
                    Código de lote
                    <input
                      maxLength={30}
                      onChange={(event) => setBatchCode(event.target.value)}
                      placeholder="PB-IPA-002"
                      required
                      value={batchCode}
                    />
                  </label>

                  <label>
                    Receta
                    <select
                      onChange={(event) => setRecipeId(event.target.value)}
                      required
                      value={recipeId}
                    >
                      <option value="">Seleccioná una receta</option>
                      {recipes.map((recipe) => (
                        <option key={recipe.id} value={recipe.id}>
                          {recipeLabel(recipe)}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="form-grid">
                  <label>
                    Volumen planificado (L)
                    <input
                      min="0.001"
                      onChange={(event) => setPlannedVolume(event.target.value)}
                      required
                      step="0.001"
                      type="number"
                      value={plannedVolume}
                    />
                  </label>

                  <label>
                    Notas
                    <input
                      onChange={(event) => setNotes(event.target.value)}
                      placeholder="Notas opcionales del lote."
                      value={notes}
                    />
                  </label>
                </div>

                <button disabled={isSaving} type="submit">
                  {isSaving ? "Creando lote..." : "Crear lote planificado"}
                </button>
              </form>
            </section>
          ) : (
            <section className="panel">
              <p className="empty-state">
                Gerencia tiene acceso de consulta a Producción.
              </p>
            </section>
          )}

          <section className="summary-grid">
            <article className="summary-card">
              <p>Lotes planificados</p>
              <strong>{plannedBatches}</strong>
            </article>

            <article className="summary-card">
              <p>Cerveza a granel disponible</p>
              <strong>{formatNumber(String(availableBulkVolume))} L</strong>
            </article>

            <article className="summary-card">
              <p>Insumos con faltante proyectado</p>
              <strong>{shortages}</strong>
            </article>
          </section>

          <section className="panel sales-panel">
            <h2>Lotes de producción</h2>

            {batches.length === 0 ? (
              <p className="empty-state">Todavía no hay lotes de producción.</p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Lote</th>
                      <th>Estilo</th>
                      <th>Estado</th>
                      <th>Volumen planificado</th>
                      <th>Volumen producido</th>
                      <th>Granel disponible</th>
                      <th>Completado</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    {batches.map((batch) => (
                      <tr key={batch.id}>
                        <td>{batch.code}</td>
                        <td>{batchStyle(batch)}</td>
                        <td>{statusLabels[batch.status]}</td>
                        <td>{formatNumber(batch.planned_volume_liters)} L</td>
                        <td>
                          {batch.produced_volume_liters
                            ? `${formatNumber(batch.produced_volume_liters)} L`
                            : "—"}
                        </td>
                        <td>
                          {formatNumber(batch.available_bulk_volume_liters)} L
                        </td>
                        <td>
                          {batch.completed_at
                            ? formatDate(batch.completed_at)
                            : "—"}
                        </td>
                        <td>
                          {batch.status === "planned" && canManageOperations ? (
                            <form
                              className="batch-completion-form"
                              onSubmit={(event) =>
                                completeProductionBatch(event, batch)
                              }
                            >
                              <input
                                aria-label={`Volumen producido de ${batch.code}`}
                                min="0.001"
                                onChange={(event) =>
                                  setCompletionVolumes((currentVolumes) => ({
                                    ...currentVolumes,
                                    [batch.id]: event.target.value,
                                  }))
                                }
                                step="0.001"
                                type="number"
                                value={
                                  completionVolumes[batch.id] ??
                                  batch.planned_volume_liters
                                }
                              />
                              <button
                                disabled={completingBatchId === batch.id}
                                type="submit"
                              >
                                {completingBatchId === batch.id
                                  ? "Completando..."
                                  : "Completar"}
                              </button>
                            </form>
                          ) : (
                            "—"
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>Proyección de materias primas</h2>

            {projections.length === 0 ? (
              <p className="empty-state">
                No hay requerimientos de producción planificados.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Insumo</th>
                      <th>Stock actual</th>
                      <th>Consumo planificado</th>
                      <th>Stock proyectado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {projections.map((projection) => (
                      <tr
                        className={
                          projection.has_shortage ? "shortage-row" : undefined
                        }
                        key={projection.raw_material_id}
                      >
                        <td>
                          {projection.raw_material_name}
                          {" · "}
                          {projection.unit_symbol}
                        </td>
                        <td>{formatNumber(projection.current_stock)}</td>
                        <td>{formatNumber(projection.planned_consumption)}</td>
                        <td>
                          {formatNumber(projection.projected_available_stock)}
                        </td>
                      </tr>
                    ))}
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

export default ProductionPage;
