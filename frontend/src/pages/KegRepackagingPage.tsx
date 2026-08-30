import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { hasRole, useCurrentUser } from "../lib/auth";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  Keg,
  KegRepackagingRun,
  PackagingFormat,
} from "../types/api";

const formatNumber = (value: string | number) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

function KegRepackagingPage() {
  const currentUser = useCurrentUser();
  const canOperate =
    hasRole(currentUser, "admin") || hasRole(currentUser, "operator");

  const [kegs, setKegs] = useState<Keg[]>([]);
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [runs, setRuns] = useState<KegRepackagingRun[]>([]);

  const [kegId, setKegId] = useState("");
  const [targetPresentationId, setTargetPresentationId] = useState("");
  const [packagedQuantity, setPackagedQuantity] = useState("");
  const [remainingVolume, setRemainingVolume] = useState("0");
  const [notes, setNotes] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);

      const [kegsData, presentationsData, formatsData, runsData] =
        await Promise.all([
          apiGet<Keg[]>("/kegs/"),
          apiGet<BeerPresentation[]>("/beer-presentations/"),
          apiGet<PackagingFormat[]>("/packaging-formats/"),
          apiGet<KegRepackagingRun[]>("/keg-repackaging-runs/"),
        ]);

      setKegs(kegsData);
      setPresentations(presentationsData);
      setFormats(formatsData);
      setRuns(runsData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos de segundo envasado.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const formatById = useMemo(
    () => new Map(formats.map((format) => [format.id, format])),
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

  const eligibleKegs = useMemo(
    () =>
      kegs.filter(
        (keg) =>
          keg.active &&
          (keg.status === "filled" || keg.status === "tapped") &&
          keg.beer_presentation_id !== null &&
          keg.production_batch_id !== null &&
          Number(keg.current_volume_liters) > 0,
      ),
    [kegs],
  );

  const selectedKeg = useMemo(
    () => eligibleKegs.find((keg) => keg.id === Number(kegId)) ?? null,
    [eligibleKegs, kegId],
  );

  const sourcePresentation = useMemo(
    () =>
      selectedKeg?.beer_presentation_id
        ? presentationById.get(selectedKeg.beer_presentation_id) ?? null
        : null,
    [presentationById, selectedKeg],
  );

  const compatibleBottlePresentations = useMemo(() => {
    if (!sourcePresentation) {
      return [];
    }

    return presentations.filter((presentation) => {
      const format = formatById.get(presentation.packaging_format_id);

      return (
        presentation.active &&
        presentation.beer_id === sourcePresentation.beer_id &&
        format?.format_type === "bottle"
      );
    });
  }, [formatById, presentations, sourcePresentation]);

  const selectedTargetPresentation = useMemo(
    () =>
      compatibleBottlePresentations.find(
        (presentation) =>
          presentation.id === Number(targetPresentationId),
      ) ?? null,
    [compatibleBottlePresentations, targetPresentationId],
  );

  const packagedVolume = useMemo(() => {
    if (!selectedTargetPresentation || !packagedQuantity) {
      return 0;
    }

    const format = formatById.get(
      selectedTargetPresentation.packaging_format_id,
    );

    return Number(format?.capacity_liters ?? 0) * Number(packagedQuantity);
  }, [
    formatById,
    packagedQuantity,
    selectedTargetPresentation,
  ]);

  const calculatedWaste = useMemo(() => {
    if (!selectedKeg || !packagedQuantity) {
      return null;
    }

    return (
      Number(selectedKeg.current_volume_liters) -
      packagedVolume -
      Number(remainingVolume || 0)
    );
  }, [packagedQuantity, packagedVolume, remainingVolume, selectedKeg]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const quantity = Number(packagedQuantity);
    const parsedRemainingVolume = Number(remainingVolume);

    if (!selectedKeg || !selectedTargetPresentation) {
      setError("Seleccioná un barril y una presentación botella.");
      return;
    }

    if (!Number.isInteger(quantity) || quantity <= 0) {
      setError("La cantidad de botellas debe ser un entero mayor a cero.");
      return;
    }

    if (
      !Number.isFinite(parsedRemainingVolume) ||
      parsedRemainingVolume < 0
    ) {
      setError("El volumen remanente debe ser un número igual o mayor a cero.");
      return;
    }

    if (
      packagedVolume + parsedRemainingVolume >
      Number(selectedKeg.current_volume_liters)
    ) {
      setError(
        "Las botellas producidas y el remanente superan el volumen del barril.",
      );
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      const run = await apiPost<KegRepackagingRun>(
        "/keg-repackaging-runs/",
        {
          keg_id: selectedKeg.id,
          target_beer_presentation_id: selectedTargetPresentation.id,
          packaged_quantity: quantity,
          remaining_volume_liters: remainingVolume,
          notes: notes.trim() || null,
        },
      );

      setKegId("");
      setTargetPresentationId("");
      setPackagedQuantity("");
      setRemainingVolume("0");
      setNotes("");

      setSuccess(
        `El segundo envasado ${run.code} fue registrado correctamente.`,
      );

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar el segundo envasado.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Operación</p>
        <h1>Embotellado</h1>
        <p>
          Convertí cerveza contenida en barriles en botellas y registrá
          automáticamente la merma del proceso.
        </p>
      </section>

      {isLoading && <p>Cargando datos de envasado...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {!isLoading && (
        <>
          {canOperate ? (
            <section className="panel sales-form-panel">
              <h2>Nuevo embotellado</h2>

              <form className="sale-form" onSubmit={handleSubmit}>
                <p className="form-help">
                  La cantidad de botellas es real. La diferencia entre el
                  volumen del barril, las botellas y el remanente se registrará
                  como merma.
                </p>

                <div className="form-grid">
                  <label>
                    Barril con cerveza
                    <select
                      onChange={(event) => {
                        setKegId(event.target.value);
                        setTargetPresentationId("");
                        setPackagedQuantity("");
                        setRemainingVolume("0");
                      }}
                      required
                      value={kegId}
                    >
                      <option value="">Seleccioná un barril</option>

                      {eligibleKegs.map((keg) => (
                        <option key={keg.id} value={keg.id}>
                          {keg.code} · {formatNumber(
                            keg.current_volume_liters,
                          )} L
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Presentación botella
                    <select
                      disabled={!selectedKeg}
                      onChange={(event) =>
                        setTargetPresentationId(event.target.value)
                      }
                      required
                      value={targetPresentationId}
                    >
                      <option value="">
                        {selectedKeg
                          ? "Seleccioná una presentación"
                          : "Seleccioná primero un barril"}
                      </option>

                      {compatibleBottlePresentations.map((presentation) => (
                        <option key={presentation.id} value={presentation.id}>
                          {presentation.code} · {presentation.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="form-grid">
                  <label>
                    Cantidad real de botellas
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

                  <label>
                    Volumen remanente en barril (L)
                    <input
                      disabled={!selectedKeg}
                      max={selectedKeg?.current_volume_liters}
                      min="0"
                      onChange={(event) =>
                        setRemainingVolume(event.target.value)
                      }
                      required
                      step="0.001"
                      type="number"
                      value={remainingVolume}
                    />
                  </label>
                </div>

                {selectedKeg && selectedTargetPresentation && (
                  <div className="form-help">
                    <p>
                      Volumen en botellas:{" "}
                      <strong>{formatNumber(packagedVolume)} L</strong>
                    </p>
                    <p>
                      Merma calculada:{" "}
                      <strong>
                        {calculatedWaste === null
                          ? "—"
                          : `${formatNumber(calculatedWaste)} L`}
                      </strong>
                    </p>
                  </div>
                )}

                <label>
                  Notas
                  <input
                    onChange={(event) => setNotes(event.target.value)}
                    placeholder="Observaciones opcionales."
                    value={notes}
                  />
                </label>

                <button
                  disabled={
                    isSaving ||
                    eligibleKegs.length === 0 ||
                    !selectedKeg ||
                    !selectedTargetPresentation
                  }
                  type="submit"
                >
                  {isSaving
                    ? "Registrando segundo envasado..."
                    : "Registrar embotellado"}
                </button>

                {eligibleKegs.length === 0 && (
                  <p className="form-help">
                    No hay barriles llenos o pinchados con cerveza disponible.
                  </p>
                )}
              </form>
            </section>
          ) : (
            <section className="panel">
              <p className="empty-state">
                Gerencia tiene acceso de consulta al historial de segundo
                envasado.
              </p>
            </section>
          )}

          <section className="panel">
            <h2>Historial de embotellados</h2>

            {runs.length === 0 ? (
              <p className="empty-state">
                Todavía no hay operaciones de envasado a botellas.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Operación</th>
                      <th>Barril</th>
                      <th>Presentación destino</th>
                      <th>Botellas</th>
                      <th>Volumen</th>
                      <th>Merma</th>
                      <th>Remanente</th>
                      <th>Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((run) => (
                      <tr key={run.id}>
                        <td>{run.code}</td>
                        <td>
                          {kegs.find((keg) => keg.id === run.keg_id)?.code ??
                            "—"}
                        </td>
                        <td>
                          {presentationById.get(
                            run.target_beer_presentation_id,
                          )?.name ?? "—"}
                        </td>
                        <td>{run.packaged_quantity}</td>
                        <td>
                          {formatNumber(run.packaged_volume_liters)} L
                        </td>
                        <td>{formatNumber(run.waste_volume_liters)} L</td>
                        <td>
                          {formatNumber(run.remaining_volume_liters)} L
                        </td>
                        <td>{formatDate(run.occurred_at)}</td>
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

export default KegRepackagingPage;