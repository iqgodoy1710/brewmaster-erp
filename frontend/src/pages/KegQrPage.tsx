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
  Beer,
  ProductionBatch,
  Recipe,
  DeliveryOrder,
  Customer,
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

  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [deliveryOrders, setDeliveryOrders] = useState<DeliveryOrder[]>([]);
  const [deliveryOrderCode, setDeliveryOrderCode] = useState("");
  const [returnVolume, setReturnVolume] = useState("0");
  const [returnNotes, setReturnNotes] = useState("");
  const [washNotes, setWashNotes] = useState("");
  const [productionBatches, setProductionBatches] = useState<ProductionBatch[]>(
    [],
  );
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [beers, setBeers] = useState<Beer[]>([]);

  const [productionBatchId, setProductionBatchId] = useState("");
  const [fillPresentationId, setFillPresentationId] = useState("");
  const [isPartialFill, setIsPartialFill] = useState(false);
  const [filledVolume, setFilledVolume] = useState("");
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
      const [
        kegData,
        formatsData,
        presentationsData,
        productionBatchesData,
        recipesData,
        beersData,
        deliveryOrdersData,
        customersData,
      ] = await Promise.all([
        apiGet<Keg>(`/kegs/by-code/${encodeURIComponent(code)}`),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<ProductionBatch[]>("/production-batches/"),
        apiGet<Recipe[]>("/recipes/"),
        apiGet<Beer[]>("/beers/"),
        apiGet<DeliveryOrder[]>("/delivery-orders/"),
        apiGet<Customer[]>("/customers/"),
      ]);

      setKeg(kegData);
      setFormats(formatsData);
      setProductionBatches(productionBatchesData);
      setRecipes(recipesData);
      setBeers(beersData);
      setPresentations(presentationsData);
      setDeliveryOrders(deliveryOrdersData);
      setCustomers(customersData);
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
      formats.find((format) => format.id === keg?.packaging_format_id) ?? null,
    [formats, keg],
  );
  const kegPresentation = useMemo(
    () =>
      presentations.find(
        (presentation) => presentation.id === keg?.beer_presentation_id,
      ) ?? null,
    [keg, presentations],
  );

  const kegBeer = useMemo(
    () => beers.find((beer) => beer.id === kegPresentation?.beer_id) ?? null,
    [beers, kegPresentation],
  );

  const kegCustomer = useMemo(
    () =>
      customers.find((customer) => customer.id === keg?.customer_id) ?? null,
    [customers, keg],
  );

  const eligibleProductionBatches = useMemo(
    () =>
      productionBatches.filter(
        (batch) =>
          batch.active &&
          (batch.status === "in_progress" ||
            (batch.status === "completed" &&
              Number(batch.available_bulk_volume_liters) > 0)),
      ),
    [productionBatches],
  );

  const selectedProductionBatch = useMemo(
    () =>
      productionBatches.find(
        (batch) => batch.id === Number(productionBatchId),
      ) ?? null,
    [productionBatchId, productionBatches],
  );

  const compatiblePresentations = useMemo(() => {
    if (!keg || !selectedProductionBatch) {
      return [];
    }

    const recipe = recipes.find(
      (item) => item.id === selectedProductionBatch.recipe_id,
    );

    if (!recipe) {
      return [];
    }

    return presentations.filter(
      (presentation) =>
        presentation.active &&
        presentation.beer_id === recipe.beer_id &&
        presentation.packaging_format_id === keg.packaging_format_id,
    );
  }, [keg, presentations, recipes, selectedProductionBatch]);

  function getProductionBatchLabel(batch: ProductionBatch): string {
    const recipe = recipes.find((item) => item.id === batch.recipe_id);

    const beer = beers.find((item) => item.id === recipe?.beer_id);

    const beerLabel = beer
      ? `${beer.name}${beer.style ? ` · ${beer.style}` : ""}`
      : "Cerveza no disponible";

    const availabilityLabel =
      batch.status === "in_progress"
        ? "En producción"
        : `Granel: ${formatVolume(batch.available_bulk_volume_liters)} L`;

    return `${batch.code} · ${beerLabel} · ${availabilityLabel}`;
  }

  const pickingDeliveryOrders = useMemo(
    () =>
      deliveryOrders.filter(
        (deliveryOrder) => deliveryOrder.status === "picking",
      ),
    [deliveryOrders],
  );

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

    if (!keg || !productionBatchId || !fillPresentationId) {
      setError("Seleccioná un lote y una presentación compatible.");
      return;
    }

    const parsedVolume = Number(filledVolume);
    const kegCapacity = Number(packagingFormat?.capacity_liters ?? 0);

    if (
      isPartialFill &&
      (!Number.isFinite(parsedVolume) ||
        parsedVolume <= 0 ||
        parsedVolume > kegCapacity)
    ) {
      setError(
        "El volumen debe ser mayor a cero y no superar la capacidad del barril.",
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      await apiPost<KegMovement>("/keg-movements/fill-from-bulk", {
        keg_id: keg.id,
        production_batch_id: Number(productionBatchId),
        beer_presentation_id: Number(fillPresentationId),
        ...(isPartialFill
          ? {
              filled_volume_liters: filledVolume,
            }
          : {}),
        notes: fillNotes.trim() || null,
      });

      setProductionBatchId("");
      setFillPresentationId("");
      setIsPartialFill(false);
      setFilledVolume("");
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

  async function assignKegToDeliveryOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!keg || !deliveryOrderCode) {
      setError("Seleccioná un pedido en preparación.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSubmitting(true);

    try {
      await apiPost(
        `/delivery-orders/${encodeURIComponent(deliveryOrderCode)}/kegs`,
        {
          keg_id: keg.id,
        },
      );

      setDeliveryOrderCode("");
      setSuccess(
        "El barril fue asignado al pedido. Se entregará al confirmar la entrega del pedido.",
      );

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo asignar el barril al pedido.",
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
                            {kegPresentation && (
                <p>
                  <strong>Cerveza:</strong>{" "}
                  {kegBeer?.name ?? kegPresentation.name}
                  {kegBeer?.style
                    ? ` · ${kegBeer.style}`
                    : ""}
                </p>
              )}

              {keg.customer_id !== null && (
                <p>
                  <strong>Cliente:</strong>{" "}
                  {kegCustomer?.name ?? "Cliente no encontrado"}
                </p>
              )}
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
          {canOperate && keg.status === "filled" && (
            <section className="panel sales-form-panel">
              <h2>Agregar barril a un pedido</h2>

              <p className="form-help">
                El pedido debe estar en preparación y tener una unidad preparada
                de la misma presentación que este barril.
              </p>

              <form className="sale-form" onSubmit={assignKegToDeliveryOrder}>
                <label>
                  Pedido en preparación
                  <select
                    onChange={(event) =>
                      setDeliveryOrderCode(event.target.value)
                    }
                    required
                    value={deliveryOrderCode}
                  >
                    <option value="">Seleccioná un pedido</option>

                    {pickingDeliveryOrders.map((deliveryOrder) => (
                      <option key={deliveryOrder.id} value={deliveryOrder.code}>
                        {deliveryOrder.code}
                      </option>
                    ))}
                  </select>
                </label>

                <button
                  disabled={isSubmitting || pickingDeliveryOrders.length === 0}
                  type="submit"
                >
                  {isSubmitting ? "Asignando..." : "Asignar al pedido"}
                </button>

                {pickingDeliveryOrders.length === 0 && (
                  <p className="form-help">
                    No hay pedidos en preparación. Creá uno, agregá la
                    presentación, iniciá el picking y luego escaneá el barril.
                  </p>
                )}
              </form>
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
                    onChange={(event) => setReturnVolume(event.target.value)}
                    required
                    step="0.001"
                    type="number"
                    value={returnVolume}
                  />
                </label>

                <label>
                  Notas
                  <input
                    onChange={(event) => setReturnNotes(event.target.value)}
                    placeholder="Observaciones opcionales."
                    value={returnNotes}
                  />
                </label>

                <button disabled={isSubmitting} type="submit">
                  {isSubmitting ? "Registrando..." : "Registrar recepción"}
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
                    onChange={(event) => setWashNotes(event.target.value)}
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
              <h2>Llenar desde lote a granel</h2>

              <p className="form-help">
                Seleccioná el lote de producción y la presentación
                correspondiente al formato de este barril.
              </p>

              <form className="sale-form" onSubmit={fillKeg}>
                <label>
                  Lote de producción
                  <select
                  className="emphasized-select"
                    onChange={(event) => {
                      setProductionBatchId(event.target.value);
                      setFillPresentationId("");
                    }}
                    required
                    value={productionBatchId}
                  >
                    <option value="">Seleccioná un lote disponible</option>

                    {eligibleProductionBatches.map((batch) => (
                      <option key={batch.id} value={batch.id}>
                        {getProductionBatchLabel(batch)}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Presentación de barril
                  <select
                    disabled={!selectedProductionBatch}
                    onChange={(event) =>
                      setFillPresentationId(event.target.value)
                    }
                    required
                    value={fillPresentationId}
                  >
                    <option value="">
                      Seleccioná una presentación compatible
                    </option>

                    {compatiblePresentations.map((presentation) => (
                      <option key={presentation.id} value={presentation.id}>
                        {presentation.code} · {presentation.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="checkbox-option">
                  <input
                    checked={isPartialFill}
                    onChange={(event) => {
                      setIsPartialFill(event.target.checked);

                      if (!event.target.checked) {
                        setFilledVolume("");
                      }
                    }}
                    type="checkbox"
                  />

                  <span>Último barril / carga parcial</span>
                </label>

                {isPartialFill && (
                  <label>
                    Volumen real a cargar (L)
                    <input
                      max={packagingFormat?.capacity_liters}
                      min="0.001"
                      onChange={(event) => setFilledVolume(event.target.value)}
                      placeholder={
                        packagingFormat
                          ? `Máximo ${formatVolume(
                              packagingFormat.capacity_liters,
                            )} L`
                          : "Volumen"
                      }
                      required
                      step="0.001"
                      type="number"
                      value={filledVolume}
                    />
                  </label>
                )}

                <label>
                  Notas
                  <input
                    onChange={(event) => setFillNotes(event.target.value)}
                    placeholder="Observaciones opcionales."
                    value={fillNotes}
                  />
                </label>

                <button
                  disabled={
                    isSubmitting || !productionBatchId || !fillPresentationId
                  }
                  type="submit"
                >
                  {isSubmitting ? "Registrando..." : "Llenar desde granel"}
                </button>

                {eligibleProductionBatches.length === 0 && (
                  <p className="form-help">
                    No hay lotes en producción ni lotes completados con granel
                    disponible.
                  </p>
                )}

                {selectedProductionBatch &&
                  compatiblePresentations.length === 0 && (
                    <p className="form-help">
                      No existe una presentación compatible con la cerveza del
                      lote y el formato de este barril.
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
