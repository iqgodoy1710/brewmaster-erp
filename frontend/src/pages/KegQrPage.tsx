import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useParams } from "react-router-dom";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import { hasRole, useCurrentUser } from "../lib/auth";
import type {
  BeerPresentation,
  Keg,
  KegMovement,
  KegStatus,
  PackagingFormat,
  PackagingRun,
} from "../types/api";

const statusLabels: Record<KegStatus, string> = {
  clean_available: "Limpio disponible",
  dirty: "Pendiente de lavado",
  filled: "Lleno en fábrica",
  at_customer: "En poder del cliente",
  tapped: "Pinchado",
  out_of_service: "Fuera de servicio",
};

const formatVolume = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

function KegQrPage() {
  const { code } = useParams();
  const currentUser = useCurrentUser();

  const canOperate =
    hasRole(currentUser, "admin") || hasRole(currentUser, "operator");

  const [keg, setKeg] = useState<Keg | null>(null);
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [packagingRuns, setPackagingRuns] = useState<PackagingRun[]>([]);
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);

  const [returnVolume, setReturnVolume] = useState("0");
  const [returnNotes, setReturnNotes] = useState("");
  const [washNotes, setWashNotes] = useState("");
  const [packagingRunId, setPackagingRunId] = useState("");
  const [fillNotes, setFillNotes] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!code) {
      setError("El código del barril no es válido.");
      setIsLoading(false);
      return;
    }

    setError(null);

    try {
      const [kegData, formatsData, runsData, presentationsData] =
        await Promise.all([
          apiGet<Keg>(`/kegs/by-code/${encodeURIComponent(code)}`),
          apiGet<PackagingFormat[]>("/packaging-formats/"),
          apiGet<PackagingRun[]>("/packaging-runs/"),
          apiGet<BeerPresentation[]>("/beer-presentations/"),
        ]);

      setKeg(kegData);
      setFormats(formatsData);
      setPackagingRuns(runsData);
      setPresentations(presentationsData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cargar el barril.",
      );
    } finally {
      setIsLoading(false);
    }
  }, [code]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const packagingFormat = useMemo(
    () =>
      formats.find(
        (format) => format.id === keg?.packaging_format_id,
      ) ?? null,
    [formats, keg],
  );

  const compatiblePackagingRuns = useMemo(() => {
    if (!keg) {
      return [];
    }

    return packagingRuns.filter((run) => {
      const presentation = presentations.find(
        (item) => item.id === run.beer_presentation_id,
      );

      return (
        run.active &&
        presentation?.packaging_format_id === keg.packaging_format_id
      );
    });
  }, [keg, packagingRuns, presentations]);

  async function receiveKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!keg) {
      return;
    }

    const volume = Number(returnVolume);
    const capacity = Number(packagingFormat?.capacity_liters ?? 0);

    if (!Number.isFinite(volume) || volume < 0 || volume > capacity) {
      setError(
        "El volumen remanente debe estar entre cero y la capacidad del barril.",
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      await apiPost<KegMovement>("/keg-movements/return", {
        keg_id: keg.id,
        resulting_volume_liters: returnVolume,
        notes: returnNotes.trim() || null,
      });

      setReturnNotes("");
      setSuccess(
        volume === 0
          ? "Barril recibido: quedó pendiente de lavado."
          : "Barril recibido con remanente de cerveza.",
      );

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar la devolución.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function washKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!keg) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      await apiPost<KegMovement>("/keg-movements/wash", {
        keg_id: keg.id,
        notes: washNotes.trim() || null,
      });

      setWashNotes("");
      setSuccess("Barril lavado y disponible para envasar.");

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar el lavado.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  async function fillKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!keg || !packagingRunId) {
      setError("Seleccioná una corrida de envasado.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      await apiPost<KegMovement>("/keg-movements/fill", {
        keg_id: keg.id,
        packaging_run_id: Number(packagingRunId),
        notes: fillNotes.trim() || null,
      });

      setPackagingRunId("");
      setFillNotes("");
      setSuccess("Barril llenado correctamente.");

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo llenar el barril.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return (
      <main className="dashboard">
        <p>Cargando barril...</p>
      </main>
    );
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Operación móvil</p>
        <h1>Gestión de barril</h1>
        <p>Escaneado desde código QR.</p>
      </section>

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

      {keg && (
        <>
          <section className="panel">
            <h2>{keg.code}</h2>

            <div className="form-grid">
              <p>
                <strong>Estado:</strong> {statusLabels[keg.status]}
              </p>
              <p>
                <strong>Formato:</strong>{" "}
                {packagingFormat
                  ? `${packagingFormat.name} · ${formatVolume(
                      packagingFormat.capacity_liters,
                    )} L`
                  : "No disponible"}
              </p>
              <p>
                <strong>Volumen actual:</strong>{" "}
                {formatVolume(keg.current_volume_liters)} L
              </p>
              <p>
                <strong>Variante:</strong> {keg.form_factor}
              </p>
            </div>
          </section>

          {!canOperate && (
            <section className="panel">
              <p className="form-help">
                Tu rol permite consultar este barril, pero no registrar
                movimientos.
              </p>
            </section>
          )}

          {canOperate && keg.status === "at_customer" && (
            <section className="panel sales-form-panel">
              <h2>Recibir barril del cliente</h2>
              <p className="form-help">
                Si vuelve vacío, ingresá 0 L: pasará a pendiente de lavado.
              </p>

              <form className="sale-form" onSubmit={receiveKeg}>
                <label>
                  Volumen remanente en litros
                  <input
                    min="0"
                    max={packagingFormat?.capacity_liters}
                    onChange={(event) =>
                      setReturnVolume(event.target.value)
                    }
                    required
                    step="0.001"
                    type="number"
                    value={returnVolume}
                  />
                </label>

                <label>
                  Notas
                  <input
                    onChange={(event) =>
                      setReturnNotes(event.target.value)
                    }
                    placeholder="Observaciones opcionales."
                    value={returnNotes}
                  />
                </label>

                <button disabled={isSubmitting} type="submit">
                  {isSubmitting
                    ? "Registrando..."
                    : "Registrar recepción"}
                </button>
              </form>
            </section>
          )}

          {canOperate && keg.status === "dirty" && (
            <section className="panel sales-form-panel">
              <h2>Registrar lavado</h2>

              <form className="sale-form" onSubmit={washKeg}>
                <label>
                  Notas
                  <input
                    onChange={(event) =>
                      setWashNotes(event.target.value)
                    }
                    placeholder="Observaciones opcionales."
                    value={washNotes}
                  />
                </label>

                <button disabled={isSubmitting} type="submit">
                  {isSubmitting ? "Registrando..." : "Marcar como lavado"}
                </button>
              </form>
            </section>
          )}

          {canOperate && keg.status === "clean_available" && (
            <section className="panel sales-form-panel">
              <h2>Llenar barril</h2>

              <form className="sale-form" onSubmit={fillKeg}>
                <label>
                  Corrida de envasado compatible
                  <select
                    onChange={(event) =>
                      setPackagingRunId(event.target.value)
                    }
                    required
                    value={packagingRunId}
                  >
                    <option value="">
                      Seleccioná una corrida de envasado
                    </option>

                    {compatiblePackagingRuns.map((run) => (
                      <option key={run.id} value={run.id}>
                        {run.code} · {formatVolume(run.packaged_volume_liters)} L
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Notas
                  <input
                    onChange={(event) =>
                      setFillNotes(event.target.value)
                    }
                    placeholder="Observaciones opcionales."
                    value={fillNotes}
                  />
                </label>

                <button
                  disabled={
                    isSubmitting || compatiblePackagingRuns.length === 0
                  }
                  type="submit"
                >
                  {isSubmitting ? "Registrando..." : "Registrar llenado"}
                </button>

                {compatiblePackagingRuns.length === 0 && (
                  <p className="form-help">
                    No hay corridas compatibles disponibles para este barril.
                  </p>
                )}
              </form>
            </section>
          )}
        </>
      )}
    </main>
  );
}

export default KegQrPage;