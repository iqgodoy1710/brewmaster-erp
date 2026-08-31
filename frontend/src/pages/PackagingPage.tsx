import { useCallback, useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  PackagingRun,
  ProductionBatch,
  Recipe,
  PackagingFormat,
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

function PackagingPage() {
  const currentUser = useCurrentUser();

  const canManageOperations = hasRole(currentUser, "admin", "operator");
  const [runs, setRuns] = useState<PackagingRun[]>([]);
  const [batches, setBatches] = useState<ProductionBatch[]>([]);
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  const [batchId, setBatchId] = useState("");
  const [presentationId, setPresentationId] = useState("");
  const [packagedQuantity, setPackagedQuantity] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [packagingFormats, setPackagingFormats] = useState<PackagingFormat[]>(
    [],
  );

  const loadPackagingData = useCallback(async () => {
    try {
      const [
        runsData,
        batchesData,
        presentationsData,
        recipesData,
        formatsData,
      ] = await Promise.all([
        apiGet<PackagingRun[]>("/packaging-runs/"),
        apiGet<ProductionBatch[]>("/production-batches/"),
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<Recipe[]>("/recipes/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
      ]);

      setRuns(runsData);
      setBatches(batchesData);
      setPresentations(presentationsData);
      setPackagingFormats(formatsData);
      setRecipes(recipesData);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos de envasado.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPackagingData();
  }, [loadPackagingData]);

  const eligibleBatches = useMemo(
    () =>
      batches.filter(
        (batch) =>
          batch.status === "in_progress" ||
          (batch.status === "completed" &&
            Number(batch.available_bulk_volume_liters) > 0),
      ),
    [batches],
  );

  const selectedBatch = useMemo(
    () => batches.find((batch) => batch.id === Number(batchId)),
    [batchId, batches],
  );

  const compatiblePresentations = useMemo(() => {
    if (!selectedBatch) {
      return [];
    }

    const recipe = recipes.find(
      (currentRecipe) => currentRecipe.id === selectedBatch.recipe_id,
    );

    if (!recipe) {
      return [];
    }

    return presentations.filter((presentation) => {
      const format = packagingFormats.find(
        (currentFormat) =>
          currentFormat.id === presentation.packaging_format_id,
      );

      return (
        presentation.beer_id === recipe.beer_id && format?.format_type === "keg"
      );
    });
  }, [packagingFormats, presentations, recipes, selectedBatch]);

  const totalPackagedVolume = useMemo(
    () =>
      runs.reduce(
        (total, run) => total + Number(run.packaged_volume_liters),
        0,
      ),
    [runs],
  );

  async function createPackagingRun(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const quantity = Number(packagedQuantity);

    if (!batchId) {
      setError("Seleccioná un lote en producción o completado.");
      return;
    }

    if (!presentationId) {
      setError("Seleccioná una presentación.");
      return;
    }

    if (!Number.isInteger(quantity) || quantity <= 0) {
      setError("La cantidad envasada debe ser un entero mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const run = await apiPost<PackagingRun>("/packaging-runs/", {
        production_batch_id: Number(batchId),
        beer_presentation_id: Number(presentationId),
        packaged_quantity: quantity,
        notes: notes.trim() || null,
      });

      setBatchId("");
      setPresentationId("");
      setPackagedQuantity("");
      setNotes("");
      setSuccess(`La corrida ${run.code} fue registrada correctamente.`);

      await loadPackagingData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar la corrida de envasado.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Operación</p>
        <h1>Embarrilado</h1>
        <p>Convertí cerveza a granel en barriles identificados.</p>
      </section>

      {isLoading && <p>Cargando datos de envasado...</p>}

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
              <h2>Nuevo embarrilado</h2>

              <form className="sale-form" onSubmit={createPackagingRun}>
                <p className="form-help">
                  El código de corrida se asignará automáticamente al registrar
                  el envasado.
                </p>

                <div className="form-grid">
                  <label>
                    Lote de producción
                    <select
                      onChange={(event) => {
                        setBatchId(event.target.value);
                        setPresentationId("");
                      }}
                      required
                      value={batchId}
                    >
                      <option value="">Seleccioná un lote</option>

                      {eligibleBatches.map((batch) => (
                        <option key={batch.id} value={batch.id}>
                          {batch.status === "in_progress"
                            ? `${batch.code} · En producción · Máximo provisional: ${formatNumber(
                                String(
                                  Number(batch.planned_volume_liters) * 1.1,
                                ),
                              )} L`
                            : `${batch.code} · Granel: ${formatNumber(
                                batch.available_bulk_volume_liters,
                              )} L`}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="form-grid">
                  <label>
                    Presentación barril de la misma cerveza
                    <select
                      disabled={!selectedBatch}
                      onChange={(event) =>
                        setPresentationId(event.target.value)
                      }
                      required
                      value={presentationId}
                    >
                      <option value="">
                        {selectedBatch
                          ? "Seleccioná una presentación"
                          : "Seleccioná primero un lote"}
                      </option>
                      {compatiblePresentations.map((presentation) => (
                        <option key={presentation.id} value={presentation.id}>
                          {presentation.code} · {presentation.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Cantidad envasada
                    <input
                      min="1"
                      onChange={(event) =>
                        setPackagedQuantity(event.target.value)
                      }
                      required
                      step="1"
                      type="number"
                      value={packagedQuantity}
                    />
                  </label>
                </div>
                {selectedBatch && compatiblePresentations.length === 0 && (
                  <p className="form-help">
                    No hay presentaciones de tipo barril configuradas para esta
                    cerveza.
                  </p>
                )}

                <label>
                  Notas
                  <input
                    onChange={(event) => setNotes(event.target.value)}
                    placeholder="Notas opcionales de la corrida."
                    value={notes}
                  />
                </label>

                <button disabled={isSaving} type="submit">
                  {isSaving
                    ? "Registrando corrida..."
                    : "Registrar embarrilado"}
                </button>
              </form>
            </section>
          ) : (
            <section className="panel">
              <p className="empty-state">
                Gerencia tiene acceso de consulta a Envasado.
              </p>
            </section>
          )}

          <section className="summary-grid">
            <article className="summary-card">
              <p>Corridas registradas</p>
              <strong>{runs.length}</strong>
            </article>

            <article className="summary-card">
              <p>Volumen total envasado</p>
              <strong>{formatNumber(String(totalPackagedVolume))} L</strong>
            </article>

            <article className="summary-card">
              <p>Lotes disponibles para envasar</p>
              <strong>{eligibleBatches.length}</strong>
            </article>
          </section>

          <section className="panel">
            <h2>Corridas de envasado</h2>

            {runs.length === 0 ? (
              <p className="empty-state">
                Todavía no hay corridas de envasado registradas.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Corrida</th>
                      <th>Lote</th>
                      <th>Presentación</th>
                      <th>Unidades</th>
                      <th>Volumen</th>
                      <th>Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((run) => {
                      const batch = batches.find(
                        (currentBatch) =>
                          currentBatch.id === run.production_batch_id,
                      );
                      const presentation = presentations.find(
                        (currentPresentation) =>
                          currentPresentation.id === run.beer_presentation_id,
                      );

                      return (
                        <tr key={run.id}>
                          <td>{run.code}</td>
                          <td>{batch?.code ?? "—"}</td>
                          <td>{presentation?.name ?? "—"}</td>
                          <td>{run.packaged_quantity}</td>
                          <td>{formatNumber(run.packaged_volume_liters)} L</td>
                          <td>{formatDate(run.occurred_at)}</td>
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

export default PackagingPage;
