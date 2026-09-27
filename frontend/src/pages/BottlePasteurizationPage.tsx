import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { hasRole, useCurrentUser } from "../lib/auth";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  BottlePasteurizationRun,
  PackagingFormat,
} from "../types/api";


const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));


function BottlePasteurizationPage() {
  const currentUser = useCurrentUser();

  const canRegister = hasRole(
    currentUser,
    "admin",
    "operator",
  );

  const [presentations, setPresentations] = useState<
    BeerPresentation[]
  >([]);

  const [formats, setFormats] = useState<PackagingFormat[]>([]);

  const [runs, setRuns] = useState<
    BottlePasteurizationRun[]
  >([]);

  const [presentationId, setPresentationId] = useState("");
  const [processedQuantity, setProcessedQuantity] = useState("");
  const [approvedQuantity, setApprovedQuantity] = useState("");
  const [notes, setNotes] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);

      const [
        presentationsData,
        formatsData,
        runsData,
      ] = await Promise.all([
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
        apiGet<BottlePasteurizationRun[]>(
          "/bottle-pasteurization-runs/",
        ),
      ]);

      setPresentations(presentationsData);
      setFormats(formatsData);
      setRuns(runsData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos de pasteurización.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const formatById = useMemo(
    () =>
      new Map(
        formats.map((format) => [format.id, format]),
      ),
    [formats],
  );

  const presentationById = useMemo(
    () =>
      new Map(
        presentations.map((presentation) => [
          presentation.id,
          presentation,
        ]),
      ),
    [presentations],
  );

  const bottlePresentations = useMemo(
    () =>
      presentations
        .filter((presentation) => {
          const packagingFormat = formatById.get(
            presentation.packaging_format_id,
          );

          return (
            presentation.active &&
            packagingFormat?.format_type === "bottle"
          );
        })
        .sort((first, second) =>
          first.name.localeCompare(second.name),
        ),
    [formatById, presentations],
  );

  const selectedPresentation = useMemo(
    () =>
      bottlePresentations.find(
        (presentation) =>
          presentation.id === Number(presentationId),
      ) ?? null,
    [bottlePresentations, presentationId],
  );

  const calculatedWaste = useMemo(() => {
    const processed = Number(processedQuantity);
    const approved = Number(approvedQuantity);

    if (
      processedQuantity === "" ||
      approvedQuantity === "" ||
      !Number.isFinite(processed) ||
      !Number.isFinite(approved)
    ) {
      return null;
    }

    return processed - approved;
  }, [approvedQuantity, processedQuantity]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const processed = Number(processedQuantity);
    const approved = Number(approvedQuantity);

    if (!selectedPresentation) {
      setError("Seleccioná una presentación de botella.");
      return;
    }

    if (!Number.isInteger(processed) || processed <= 0) {
      setError(
        "La cantidad procesada debe ser un entero mayor a cero.",
      );
      return;
    }

    if (!Number.isInteger(approved) || approved < 0) {
      setError(
        "La cantidad aprobada debe ser un entero igual o mayor a cero.",
      );
      return;
    }

    if (approved > processed) {
      setError(
        "La cantidad aprobada no puede superar la cantidad procesada.",
      );
      return;
    }

    if (processed > selectedPresentation.current_stock) {
      setError(
        "La cantidad procesada supera el stock disponible.",
      );
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      const run = await apiPost<BottlePasteurizationRun>(
        "/bottle-pasteurization-runs/",
        {
          beer_presentation_id: selectedPresentation.id,
          processed_quantity: processed,
          approved_quantity: approved,
          notes: notes.trim() || null,
        },
      );

      setPresentationId("");
      setProcessedQuantity("");
      setApprovedQuantity("");
      setNotes("");

      setSuccess(
        `La pasteurización ${run.code} fue registrada. ` +
          `Merma descontada: ${run.waste_quantity} botella(s).`,
      );

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar la pasteurización.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Operación</p>
        <h1>Pasteurización</h1>
        <p>
          Registrá las botellas procesadas, aprobadas y descartadas.
          Solamente la merma se descuenta del stock.
        </p>
      </section>

      {isLoading && <p>Cargando pasteurizaciones...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && (
        <p className="success-message" role="status">
          {success}
        </p>
      )}

      {!isLoading && (
        <>
          {canRegister ? (
            <section className="panel sales-form-panel">
              <h2>Nueva pasteurización</h2>

              <form
                className="sale-form"
                onSubmit={handleSubmit}
              >
                <label>
                  Presentación de botella
                  <select
                    onChange={(event) => {
                      setPresentationId(event.target.value);
                      setProcessedQuantity("");
                      setApprovedQuantity("");
                    }}
                    required
                    value={presentationId}
                  >
                    <option value="">
                      Seleccioná una presentación
                    </option>

                    {bottlePresentations.map(
                      (presentation) => (
                        <option
                          key={presentation.id}
                          value={presentation.id}
                        >
                          {presentation.code} · {presentation.name} ·
                          Stock: {presentation.current_stock}
                        </option>
                      ),
                    )}
                  </select>
                </label>

                {selectedPresentation && (
                  <p className="form-help">
                    Stock disponible:{" "}
                    <strong>
                      {selectedPresentation.current_stock} botellas
                    </strong>
                  </p>
                )}

                <div className="form-grid">
                  <label>
                    Botellas procesadas
                    <input
                      max={
                        selectedPresentation?.current_stock
                      }
                      min="1"
                      onChange={(event) =>
                        setProcessedQuantity(event.target.value)
                      }
                      required
                      step="1"
                      type="number"
                      value={processedQuantity}
                    />
                  </label>

                  <label>
                    Botellas aprobadas
                    <input
                      max={processedQuantity || undefined}
                      min="0"
                      onChange={(event) =>
                        setApprovedQuantity(event.target.value)
                      }
                      required
                      step="1"
                      type="number"
                      value={approvedQuantity}
                    />
                  </label>
                </div>

                <p className="form-help">
                  Merma calculada:{" "}
                  <strong>
                    {calculatedWaste === null ||
                    calculatedWaste < 0
                      ? "—"
                      : `${calculatedWaste} botella(s)`}
                  </strong>
                </p>

                <label>
                  Notas
                  <input
                    onChange={(event) =>
                      setNotes(event.target.value)
                    }
                    placeholder="Observaciones opcionales."
                    value={notes}
                  />
                </label>

                <button
                  disabled={
                    isSaving ||
                    !selectedPresentation ||
                    calculatedWaste === null ||
                    calculatedWaste < 0
                  }
                  type="submit"
                >
                  {isSaving
                    ? "Registrando..."
                    : "Registrar pasteurización"}
                </button>
              </form>
            </section>
          ) : (
            <section className="panel">
              <p className="empty-state">
                Tenés acceso de consulta al historial de
                pasteurizaciones.
              </p>
            </section>
          )}

          <section className="panel">
            <h2>Historial de pasteurizaciones</h2>

            {runs.length === 0 ? (
              <p className="empty-state">
                Todavía no hay pasteurizaciones registradas.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Operación</th>
                      <th>Presentación</th>
                      <th>Procesadas</th>
                      <th>Aprobadas</th>
                      <th>Merma</th>
                      <th>Fecha</th>
                      <th>Notas</th>
                    </tr>
                  </thead>

                  <tbody>
                    {runs.map((run) => (
                      <tr key={run.id}>
                        <td>{run.code}</td>
                        <td>
                          {presentationById.get(
                            run.beer_presentation_id,
                          )?.name ?? "—"}
                        </td>
                        <td>{run.processed_quantity}</td>
                        <td>{run.approved_quantity}</td>
                        <td>{run.waste_quantity}</td>
                        <td>{formatDate(run.occurred_at)}</td>
                        <td>{run.notes ?? "—"}</td>
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

export default BottlePasteurizationPage;