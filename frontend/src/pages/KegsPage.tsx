import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { hasRole, useCurrentUser } from "../lib/auth";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  Keg,
  KegFormFactor,
  KegMovement,
  KegMovementType,
  KegRemnantTransferResponse,
  KegStatus,
  PackagingFormat,
  PackagingRun,
  ProductionBatch,
  Recipe,
} from "../types/api";
import { Link } from "react-router-dom";

const formFactorLabels: Record<KegFormFactor, string> = {
  standard: "Estándar",
  flat: "Flat",
  slim: "Slim",
};

const statusLabels: Record<KegStatus, string> = {
  clean_available: "Limpio disponible",
  dirty: "Pendiente de lavado",
  filled: "Lleno en fábrica",
  at_customer: "En poder del cliente",
  tapped: "Pinchado",
  out_of_service: "Fuera de servicio",
};

const movementTypeLabels: Record<KegMovementType, string> = {
  filling: "Llenado",
  delivery: "Entrega",
  return: "Devolución",
  washing: "Lavado",
  tapping: "Pinchado",
  remnant_transfer: "Recuperación de remanente",
  inventory_adjustment: "Ajuste de inventario",
  out_of_service: "Fuera de servicio",
  repackaging: "Envasado a botellas",
};

const formatVolume = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

function KegsPage() {
  const currentUser = useCurrentUser();

  const canOperateKegs =
    hasRole(currentUser, "admin") || hasRole(currentUser, "operator");
  const canRegisterKegs = hasRole(currentUser, "admin");

  const [kegs, setKegs] = useState<Keg[]>([]);
  const [kegFormats, setKegFormats] = useState<PackagingFormat[]>([]);

  const [selectedKegId, setSelectedKegId] = useState("");
  const [movements, setMovements] = useState<KegMovement[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);

  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [packagingRuns, setPackagingRuns] = useState<PackagingRun[]>([]);
  const [productionBatches, setProductionBatches] = useState<ProductionBatch[]>(
    [],
  );
  const [recipes, setRecipes] = useState<Recipe[]>([]);

  const [directFillKegId, setDirectFillKegId] = useState("");
  const [directProductionBatchId, setDirectProductionBatchId] = useState("");
  const [directPresentationId, setDirectPresentationId] = useState("");
  const [directFillNotes, setDirectFillNotes] = useState("");
  const [isDirectFilling, setIsDirectFilling] = useState(false);
  const [fillKegId, setFillKegId] = useState("");
  const [fillPackagingRunId, setFillPackagingRunId] = useState("");
  const [fillNotes, setFillNotes] = useState("");
  const [isFilling, setIsFilling] = useState(false);
  const [code, setCode] = useState("");
  const [packagingFormatId, setPackagingFormatId] = useState("");
  const [formFactor, setFormFactor] = useState<KegFormFactor>("standard");
  const [notes, setNotes] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const [returnKegId, setReturnKegId] = useState("");
  const [returnVolume, setReturnVolume] = useState("0");
  const [returnNotes, setReturnNotes] = useState("");
  const [isReturning, setIsReturning] = useState(false);

  const [washKegId, setWashKegId] = useState("");
  const [washNotes, setWashNotes] = useState("");
  const [isWashing, setIsWashing] = useState(false);

  const [selectedRemnantKegIds, setSelectedRemnantKegIds] = useState<number[]>(
    [],
  );
  const [remnantNotes, setRemnantNotes] = useState("");
  const [isTransferringRemnants, setIsTransferringRemnants] = useState(false);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [
        kegsData,
        formatsData,
        presentationsData,
        runsData,
        batchesData,
        recipesData,
      ] = await Promise.all([
        apiGet<Keg[]>("/kegs/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<PackagingRun[]>("/packaging-runs/"),
        apiGet<ProductionBatch[]>("/production-batches/"),
        apiGet<Recipe[]>("/recipes/"),
      ]);

      setKegs(kegsData);
      setKegFormats(
        formatsData.filter((format) => format.format_type === "keg"),
      );
      setPresentations(presentationsData);
      setPackagingRuns(runsData);
      setProductionBatches(batchesData);
      setRecipes(recipesData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los barriles.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadKegMovements = useCallback(async (kegId: string) => {
    if (!kegId) {
      setMovements([]);
      return;
    }

    setIsHistoryLoading(true);

    try {
      const data = await apiGet<KegMovement[]>(
        `/kegs/${encodeURIComponent(kegId)}/movements`,
      );

      setMovements(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cargar el historial del barril.",
      );
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    void loadKegMovements(selectedKegId);
  }, [loadKegMovements, selectedKegId]);

  const customerKegs = useMemo(
    () => kegs.filter((keg) => keg.active && keg.status === "at_customer"),
    [kegs],
  );

  const dirtyKegs = useMemo(
    () => kegs.filter((keg) => keg.active && keg.status === "dirty"),
    [kegs],
  );

  const tappedKegs = useMemo(
    () =>
      kegs.filter(
        (keg) =>
          keg.active &&
          keg.status === "tapped" &&
          Number(keg.current_volume_liters) > 0,
      ),
    [kegs],
  );
  const cleanKegs = useMemo(
    () => kegs.filter((keg) => keg.active && keg.status === "clean_available"),
    [kegs],
  );

  const selectedFillKeg = useMemo(
    () => cleanKegs.find((keg) => keg.id === Number(fillKegId)) ?? null,
    [cleanKegs, fillKegId],
  );

  const compatiblePackagingRuns = useMemo(() => {
    if (!selectedFillKeg) {
      return [];
    }

    return packagingRuns.filter((run) => {
      const presentation = presentations.find(
        (item) => item.id === run.beer_presentation_id,
      );

      return (
        run.active &&
        presentation?.packaging_format_id ===
          selectedFillKeg.packaging_format_id
      );
    });
  }, [packagingRuns, presentations, selectedFillKeg]);

  const eligibleDirectFillBatches = useMemo(
    () =>
      productionBatches.filter(
        (batch) =>
          batch.status === "in_progress" ||
          (batch.status === "completed" &&
            Number(batch.available_bulk_volume_liters) > 0),
      ),
    [productionBatches],
  );

  const selectedDirectFillKeg = useMemo(
    () => cleanKegs.find((keg) => keg.id === Number(directFillKegId)) ?? null,
    [cleanKegs, directFillKegId],
  );

  const selectedDirectProductionBatch = useMemo(
    () =>
      productionBatches.find(
        (batch) => batch.id === Number(directProductionBatchId),
      ) ?? null,
    [directProductionBatchId, productionBatches],
  );

  const directCompatiblePresentations = useMemo(() => {
    if (!selectedDirectFillKeg || !selectedDirectProductionBatch) {
      return [];
    }

    const recipe = recipes.find(
      (currentRecipe) =>
        currentRecipe.id === selectedDirectProductionBatch.recipe_id,
    );

    if (!recipe) {
      return [];
    }

    return presentations.filter(
      (presentation) =>
        presentation.active &&
        presentation.beer_id === recipe.beer_id &&
        presentation.packaging_format_id ===
          selectedDirectFillKeg.packaging_format_id,
    );
  }, [
    presentations,
    recipes,
    selectedDirectFillKeg,
    selectedDirectProductionBatch,
  ]);

  const selectedReturnKeg = useMemo(
    () => customerKegs.find((keg) => keg.id === Number(returnKegId)) ?? null,
    [customerKegs, returnKegId],
  );

  function getFormatLabel(packagingFormatIdValue: number) {
    const format = kegFormats.find(
      (item) => item.id === packagingFormatIdValue,
    );

    if (!format) {
      return "Formato no disponible";
    }

    return `${format.name} · ${formatVolume(format.capacity_liters)} L`;
  }

  function getKegCapacity(keg: Keg): number {
    const format = kegFormats.find(
      (item) => item.id === keg.packaging_format_id,
    );

    return format ? Number(format.capacity_liters) : 0;
  }

  async function refreshData() {
    await loadData();

    if (selectedKegId) {
      await loadKegMovements(selectedKegId);
    }
  }

  async function createKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!code.trim() || !packagingFormatId) {
      setError("Ingresá el identificador y seleccioná un formato de barril.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const keg = await apiPost<Keg>("/kegs/", {
        code: code.trim(),
        packaging_format_id: Number(packagingFormatId),
        form_factor: formFactor,
        notes: notes.trim() || null,
      });

      setCode("");
      setPackagingFormatId("");
      setFormFactor("standard");
      setNotes("");
      setSuccess(`El barril ${keg.code} fue registrado correctamente.`);

      await refreshData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar el barril.",
      );
    } finally {
      setIsSaving(false);
    }
  }
  async function fillKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!fillKegId || !fillPackagingRunId) {
      setError("Seleccioná un barril limpio y una corrida de envasado.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsFilling(true);

    try {
      const movement = await apiPost<KegMovement>("/keg-movements/fill", {
        keg_id: Number(fillKegId),
        packaging_run_id: Number(fillPackagingRunId),
        notes: fillNotes.trim() || null,
      });

      setFillKegId("");
      setFillPackagingRunId("");
      setFillNotes("");
      setSelectedKegId(String(movement.keg_id));
      setSuccess("El barril fue llenado y quedó disponible para entregar.");

      await loadData();
      await loadKegMovements(String(movement.keg_id));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo llenar el barril.",
      );
    } finally {
      setIsFilling(false);
    }
  }

  async function fillKegFromBulk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!directFillKegId || !directProductionBatchId || !directPresentationId) {
      setError("Seleccioná un barril limpio, un lote y una presentación.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsDirectFilling(true);

    try {
      const movement = await apiPost<KegMovement>(
        "/keg-movements/fill-from-bulk",
        {
          keg_id: Number(directFillKegId),
          production_batch_id: Number(directProductionBatchId),
          beer_presentation_id: Number(directPresentationId),
          notes: directFillNotes.trim() || null,
        },
      );

      setDirectFillKegId("");
      setDirectProductionBatchId("");
      setDirectPresentationId("");
      setDirectFillNotes("");
      setSelectedKegId(String(movement.keg_id));
      setSuccess(
        "El barril fue llenado directamente desde el lote de producción.",
      );

      await loadData();
      await loadKegMovements(String(movement.keg_id));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo llenar el barril desde granel.",
      );
    } finally {
      setIsDirectFilling(false);
    }
  }

  async function returnKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedReturnKeg) {
      setError("Seleccioná un barril entregado a un cliente.");
      return;
    }

    const parsedVolume = Number(returnVolume);
    const capacity = getKegCapacity(selectedReturnKeg);

    if (!Number.isFinite(parsedVolume) || parsedVolume < 0) {
      setError("El volumen remanente debe ser un número igual o mayor a cero.");
      return;
    }

    if (parsedVolume > capacity) {
      setError(
        `El volumen remanente no puede superar la capacidad de ${formatVolume(
          String(capacity),
        )} L.`,
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setIsReturning(true);

    try {
      const movement = await apiPost<KegMovement>("/keg-movements/return", {
        keg_id: selectedReturnKeg.id,
        resulting_volume_liters: returnVolume,
        notes: returnNotes.trim() || null,
      });

      setReturnKegId("");
      setReturnVolume("0");
      setReturnNotes("");
      setSelectedKegId(String(movement.keg_id));
      setSuccess(
        parsedVolume > 0
          ? `El barril fue devuelto con ${formatVolume(
              returnVolume,
            )} L de remanente.`
          : "El barril fue devuelto vacío y quedó pendiente de lavado.",
      );

      await refreshData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar la devolución.",
      );
    } finally {
      setIsReturning(false);
    }
  }

  async function washKeg(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!washKegId) {
      setError("Seleccioná un barril pendiente de lavado.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsWashing(true);

    try {
      const movement = await apiPost<KegMovement>("/keg-movements/wash", {
        keg_id: Number(washKegId),
        notes: washNotes.trim() || null,
      });

      setWashKegId("");
      setWashNotes("");
      setSelectedKegId(String(movement.keg_id));
      setSuccess("El barril fue marcado como limpio y disponible.");

      await refreshData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar el lavado.",
      );
    } finally {
      setIsWashing(false);
    }
  }

  function toggleRemnantKeg(kegId: number) {
    setSelectedRemnantKegIds((currentIds) =>
      currentIds.includes(kegId)
        ? currentIds.filter((id) => id !== kegId)
        : [...currentIds, kegId],
    );
  }

  async function transferRemnants(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (selectedRemnantKegIds.length === 0) {
      setError("Seleccioná al menos un barril pinchado.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsTransferringRemnants(true);

    try {
      const result = await apiPost<KegRemnantTransferResponse>(
        "/keg-movements/transfer-remnants",
        {
          source_keg_ids: selectedRemnantKegIds,
          notes: remnantNotes.trim() || null,
        },
      );

      setSelectedRemnantKegIds([]);
      setRemnantNotes("");
      setSuccess(
        `Se recuperaron ${formatVolume(
          result.recovered_volume_liters,
        )} L para el lote de producción.`,
      );

      await refreshData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron recuperar los remanentes.",
      );
    } finally {
      setIsTransferringRemnants(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Operación</p>
        <h1>Barriles</h1>
        <p>
          Registrá, entregá, recuperá y consultá los barriles retornables de la
          cervecería.
        </p>
      </section>

      {isLoading && <p>Cargando barriles...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {!isLoading && (
        <>
          {canOperateKegs && (
            <>
              {canRegisterKegs && (
                <section className="panel sales-form-panel">
                  <h2>Registrar barril</h2>

                  <form className="sale-form" onSubmit={createKeg}>
                    <div className="form-grid">
                      <label>
                        Identificador físico
                        <input
                          maxLength={50}
                          onChange={(event) => setCode(event.target.value)}
                          placeholder="K20-F-001"
                          required
                          value={code}
                        />
                      </label>

                      <label>
                        Formato de barril
                        <select
                          onChange={(event) =>
                            setPackagingFormatId(event.target.value)
                          }
                          required
                          value={packagingFormatId}
                        >
                          <option value="">Seleccioná un formato</option>

                          {kegFormats.map((format) => (
                            <option key={format.id} value={format.id}>
                              {format.name} ·{" "}
                              {formatVolume(format.capacity_liters)} L
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>

                    <div className="form-grid">
                      <label>
                        Variante física
                        <select
                          onChange={(event) =>
                            setFormFactor(event.target.value as KegFormFactor)
                          }
                          value={formFactor}
                        >
                          <option value="standard">Estándar</option>
                          <option value="flat">Flat</option>
                          <option value="slim">Slim</option>
                        </select>
                      </label>

                      <label>
                        Notas
                        <input
                          onChange={(event) => setNotes(event.target.value)}
                          placeholder="Observaciones opcionales."
                          value={notes}
                        />
                      </label>
                    </div>

                    <button
                      disabled={isSaving || kegFormats.length === 0}
                      type="submit"
                    >
                      {isSaving ? "Registrando barril..." : "Registrar barril"}
                    </button>

                    {kegFormats.length === 0 && (
                      <p className="form-help">
                        Primero registrá un formato de tipo Barril.
                      </p>
                    )}
                  </form>
                </section>
              )}
              <section className="panel sales-form-panel">
                <h2>Llenar barril</h2>

                <p className="form-help">
                  Seleccioná un barril limpio y una corrida compatible de
                  envasado.
                </p>

                <form className="sale-form" onSubmit={fillKeg}>
                  <div className="form-grid">
                    <label>
                      Barril limpio
                      <select
                        onChange={(event) => {
                          setFillKegId(event.target.value);
                          setFillPackagingRunId("");
                        }}
                        required
                        value={fillKegId}
                      >
                        <option value="">Seleccioná un barril</option>

                        {cleanKegs.map((keg) => (
                          <option key={keg.id} value={keg.id}>
                            {keg.code} ·{" "}
                            {getFormatLabel(keg.packaging_format_id)}
                            {keg.form_factor !== "standard" &&
                              ` · ${formFactorLabels[keg.form_factor]}`}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Corrida de envasado compatible
                      <select
                        disabled={!selectedFillKeg}
                        onChange={(event) =>
                          setFillPackagingRunId(event.target.value)
                        }
                        required
                        value={fillPackagingRunId}
                      >
                        <option value="">
                          {selectedFillKeg
                            ? "Seleccioná una corrida"
                            : "Seleccioná primero un barril"}
                        </option>

                        {compatiblePackagingRuns.map((run) => (
                          <option key={run.id} value={run.id}>
                            {run.code} · {run.packaged_quantity} unidades
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <label>
                    Notas
                    <input
                      onChange={(event) => setFillNotes(event.target.value)}
                      placeholder="Observaciones opcionales del llenado."
                      value={fillNotes}
                    />
                  </label>

                  <button
                    disabled={
                      isFilling ||
                      cleanKegs.length === 0 ||
                      !selectedFillKeg ||
                      compatiblePackagingRuns.length === 0
                    }
                    type="submit"
                  >
                    {isFilling ? "Llenando barril..." : "Registrar llenado"}
                  </button>

                  {cleanKegs.length === 0 && (
                    <p className="form-help">
                      No hay barriles limpios disponibles para llenar.
                    </p>
                  )}

                  {selectedFillKeg && compatiblePackagingRuns.length === 0 && (
                    <p className="form-help">
                      No hay corridas compatibles disponibles para este formato.
                    </p>
                  )}
                </form>
              </section>

              <section className="panel sales-form-panel">
                <h2>Llenar desde lote a granel</h2>

                <p className="form-help">
                  Genera automáticamente una corrida de una unidad y la asigna
                  al barril físico seleccionado.
                </p>

                <form className="sale-form" onSubmit={fillKegFromBulk}>
                  <div className="form-grid">
                    <label>
                      Barril limpio
                      <select
                        onChange={(event) => {
                          setDirectFillKegId(event.target.value);
                          setDirectPresentationId("");
                        }}
                        required
                        value={directFillKegId}
                      >
                        <option value="">Seleccioná un barril</option>
                        {cleanKegs.map((keg) => (
                          <option key={keg.id} value={keg.id}>
                            {keg.code} ·{" "}
                            {getFormatLabel(keg.packaging_format_id)}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Lote de producción
                      <select
                        onChange={(event) => {
                          setDirectProductionBatchId(event.target.value);
                          setDirectPresentationId("");
                        }}
                        required
                        value={directProductionBatchId}
                      >
                        <option value="">Seleccioná un lote</option>
                        {eligibleDirectFillBatches.map((batch) => (
                          <option key={batch.id} value={batch.id}>
                            {batch.code} ·{" "}
                            {batch.status === "in_progress"
                              ? "En producción"
                              : `Granel: ${formatVolume(
                                  batch.available_bulk_volume_liters,
                                )} L`}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <label>
                    Presentación de barril
                    <select
                      disabled={
                        !selectedDirectFillKeg || !selectedDirectProductionBatch
                      }
                      onChange={(event) =>
                        setDirectPresentationId(event.target.value)
                      }
                      required
                      value={directPresentationId}
                    >
                      <option value="">
                        Seleccioná una presentación compatible
                      </option>
                      {directCompatiblePresentations.map((presentation) => (
                        <option key={presentation.id} value={presentation.id}>
                          {presentation.code} · {presentation.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Notas
                    <input
                      onChange={(event) =>
                        setDirectFillNotes(event.target.value)
                      }
                      placeholder="Observaciones opcionales del llenado."
                      value={directFillNotes}
                    />
                  </label>

                  <button
                    disabled={
                      isDirectFilling ||
                      !selectedDirectFillKeg ||
                      !selectedDirectProductionBatch ||
                      directCompatiblePresentations.length === 0
                    }
                    type="submit"
                  >
                    {isDirectFilling
                      ? "Llenando barril..."
                      : "Llenar desde granel"}
                  </button>
                </form>
              </section>

              <section className="panel sales-form-panel">
                <h2>Registrar devolución</h2>

                <form className="sale-form" onSubmit={returnKeg}>
                  <div className="form-grid">
                    <label>
                      Barril entregado
                      <select
                        onChange={(event) => setReturnKegId(event.target.value)}
                        required
                        value={returnKegId}
                      >
                        <option value="">
                          Seleccioná un barril en poder del cliente
                        </option>

                        {customerKegs.map((keg) => (
                          <option key={keg.id} value={keg.id}>
                            {keg.code} ·{" "}
                            {formatVolume(keg.current_volume_liters)} L
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Volumen remanente (L)
                      <input
                        min="0"
                        onChange={(event) =>
                          setReturnVolume(event.target.value)
                        }
                        step="0.001"
                        type="number"
                        value={returnVolume}
                      />
                    </label>
                  </div>

                  <label>
                    Notas
                    <input
                      onChange={(event) => setReturnNotes(event.target.value)}
                      placeholder="Observaciones opcionales de la devolución."
                      value={returnNotes}
                    />
                  </label>

                  <button
                    disabled={isReturning || customerKegs.length === 0}
                    type="submit"
                  >
                    {isReturning
                      ? "Registrando devolución..."
                      : "Registrar devolución"}
                  </button>

                  {customerKegs.length === 0 && (
                    <p className="form-help">
                      No hay barriles actualmente en poder de clientes.
                    </p>
                  )}
                </form>
              </section>

              <section className="panel sales-form-panel">
                <h2>Registrar lavado</h2>

                <form className="sale-form" onSubmit={washKeg}>
                  <div className="form-grid">
                    <label>
                      Barril pendiente de lavado
                      <select
                        onChange={(event) => setWashKegId(event.target.value)}
                        required
                        value={washKegId}
                      >
                        <option value="">Seleccioná un barril sucio</option>

                        {dirtyKegs.map((keg) => (
                          <option key={keg.id} value={keg.id}>
                            {keg.code} ·{" "}
                            {getFormatLabel(keg.packaging_format_id)}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Notas
                      <input
                        onChange={(event) => setWashNotes(event.target.value)}
                        placeholder="Observaciones opcionales del lavado."
                        value={washNotes}
                      />
                    </label>
                  </div>

                  <button
                    disabled={isWashing || dirtyKegs.length === 0}
                    type="submit"
                  >
                    {isWashing ? "Registrando lavado..." : "Registrar lavado"}
                  </button>

                  {dirtyKegs.length === 0 && (
                    <p className="form-help">
                      No hay barriles pendientes de lavado.
                    </p>
                  )}
                </form>
              </section>

              <section className="panel sales-form-panel">
                <h2>Recuperar remanentes</h2>

                <p className="form-help">
                  Los barriles seleccionados deben contener la misma cerveza y
                  provenir del mismo lote de producción. El volumen recuperado
                  vuelve a estar disponible como cerveza a granel.
                </p>

                <form className="sale-form" onSubmit={transferRemnants}>
                  {tappedKegs.length === 0 ? (
                    <p className="empty-state">
                      No hay barriles pinchados con remanente disponible.
                    </p>
                  ) : (
                    <div className="checkbox-list">
                      {tappedKegs.map((keg) => {
                        const isSelected = selectedRemnantKegIds.includes(
                          keg.id,
                        );

                        return (
                          <label key={keg.id} className="checkbox-option">
                            <input
                              checked={isSelected}
                              onChange={() => toggleRemnantKeg(keg.id)}
                              type="checkbox"
                            />

                            <span>
                              <strong>{keg.code}</strong>
                              {" · "}
                              {formatVolume(keg.current_volume_liters)} L{" · "}
                              {getFormatLabel(keg.packaging_format_id)}
                            </span>
                          </label>
                        );
                      })}
                    </div>
                  )}

                  <label>
                    Notas
                    <input
                      onChange={(event) => setRemnantNotes(event.target.value)}
                      placeholder="Observaciones opcionales."
                      value={remnantNotes}
                    />
                  </label>

                  <button
                    disabled={
                      isTransferringRemnants ||
                      selectedRemnantKegIds.length === 0
                    }
                    type="submit"
                  >
                    {isTransferringRemnants
                      ? "Recuperando remanentes..."
                      : "Recuperar remanentes"}
                  </button>
                </form>
              </section>
            </>
          )}

          <section className="panel">
            <h2>Barriles registrados</h2>
            {canOperateKegs && (
              <Link className="inline-link-button" to="/barriles/etiquetas">
                Imprimir etiquetas QR
              </Link>
            )}
            {kegs.length === 0 ? (
              <p className="empty-state">
                Todavía no hay barriles registrados.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Identificador</th>
                      <th>Formato</th>
                      <th>Variante</th>
                      <th>Estado</th>
                      <th>Volumen actual</th>
                      <th>Etiqueta</th>
                    </tr>
                  </thead>

                  <tbody>
                    {kegs.map((keg) => (
                      <tr key={keg.id}>
                        <td>{keg.code}</td>
                        <td>{getFormatLabel(keg.packaging_format_id)}</td>
                        <td>{formFactorLabels[keg.form_factor]}</td>
                        <td>{statusLabels[keg.status]}</td>
                        <td>{formatVolume(keg.current_volume_liters)} L</td>
                        <td>
                          <Link
                            className="inline-link-button"
                            to={`/barriles/etiqueta/${encodeURIComponent(keg.code)}`}
                          >
                            Ver QR
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>Historial del barril</h2>

            <label>
              Barril
              <select
                onChange={(event) => setSelectedKegId(event.target.value)}
                value={selectedKegId}
              >
                <option value="">Seleccioná un barril</option>

                {kegs.map((keg) => (
                  <option key={keg.id} value={keg.id}>
                    {keg.code} · {statusLabels[keg.status]}
                  </option>
                ))}
              </select>
            </label>

            {isHistoryLoading && <p>Cargando historial...</p>}

            {!isHistoryLoading && selectedKegId && (
              <>
                {movements.length === 0 ? (
                  <p className="empty-state">
                    Todavía no hay movimientos para este barril.
                  </p>
                ) : (
                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          <th>Fecha</th>
                          <th>Movimiento</th>
                          <th>Estado</th>
                          <th>Volumen resultante</th>
                          <th>Referencia</th>
                          <th>Operador</th>
                        </tr>
                      </thead>

                      <tbody>
                        {movements.map((movement) => (
                          <tr key={movement.id}>
                            <td>{formatDate(movement.occurred_at)}</td>
                            <td>
                              {movementTypeLabels[movement.movement_type]}
                            </td>
                            <td>
                              {statusLabels[movement.previous_status]}
                              {" → "}
                              {statusLabels[movement.new_status]}
                            </td>
                            <td>
                              {formatVolume(movement.resulting_volume_liters)} L
                            </td>
                            <td>{movement.reference ?? "—"}</td>
                            <td>
                              {movement.performed_by_username ??
                                "Sistema / histórico"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </section>
        </>
      )}
    </main>
  );
}

export default KegsPage;
