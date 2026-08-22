import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  BeerPresentationPrice,
  CompletedSaleReportItem,
  Customer,
  Keg,
  PackagingFormat,
  Sale,
  SaleItem,
} from "../types/api";

type SaleLine = {
  beerPresentationId: number;
  beerPresentationCode: string;
  beerPresentationName: string;
  quantity: number;
  unitPrice: string;
};

const formatCurrency = (amount: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
    currencyDisplay: "narrowSymbol",
  }).format(Number(amount));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

const kegFormFactorLabels = {
  standard: "Estándar",
  flat: "Flat",
  slim: "Slim",
};

function SalesPage() {
  const [sales, setSales] = useState<CompletedSaleReportItem[]>([]);
  const [allSales, setAllSales] = useState<Sale[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [packagingFormats, setPackagingFormats] = useState<
    PackagingFormat[]
  >([]);
  const [kegs, setKegs] = useState<Keg[]>([]);

  const [lines, setLines] = useState<SaleLine[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [notes, setNotes] = useState("");
  const [presentationId, setPresentationId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [activePrice, setActivePrice] =
    useState<BeerPresentationPrice | null>(null);
  const [isPriceLoading, setIsPriceLoading] = useState(false);

  const [createdSale, setCreatedSale] = useState<Sale | null>(null);
  const [selectedKegIds, setSelectedKegIds] = useState<number[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);

  const [saleToCancelCode, setSaleToCancelCode] = useState("");
  const [cancellationReason, setCancellationReason] = useState("");
  const [isCancelling, setIsCancelling] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [
        salesData,
        allSalesData,
        customersData,
        presentationsData,
        packagingFormatsData,
        kegsData,
      ] = await Promise.all([
        apiGet<CompletedSaleReportItem[]>("/sales/report"),
        apiGet<Sale[]>("/sales/"),
        apiGet<Customer[]>("/customers/"),
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
        apiGet<Keg[]>("/kegs/"),
      ]);

      setSales(salesData);
      setAllSales(allSalesData);
      setCustomers(customersData);
      setPresentations(presentationsData);
      setPackagingFormats(packagingFormatsData);
      setKegs(kegsData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los datos comerciales.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  useEffect(() => {
    async function loadActivePrice() {
      if (!presentationId) {
        setActivePrice(null);
        return;
      }

      setIsPriceLoading(true);
      setActivePrice(null);

      try {
        const prices = await apiGet<BeerPresentationPrice[]>(
          `/beer-presentations/${presentationId}/prices`,
        );

        setActivePrice(prices.find((price) => price.active) ?? null);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudo cargar el precio de la presentación.",
        );
      } finally {
        setIsPriceLoading(false);
      }
    }

    void loadActivePrice();
  }, [presentationId]);

  const totalUnits = useMemo(
    () => sales.reduce((total, sale) => total + sale.total_units, 0),
    [sales],
  );

  const totalAmount = useMemo(
    () => sales.reduce((total, sale) => total + Number(sale.total_amount), 0),
    [sales],
  );

  const draftTotal = useMemo(
    () =>
      lines.reduce(
        (total, line) => total + line.quantity * Number(line.unitPrice),
        0,
      ),
    [lines],
  );

  const cancellableSales = useMemo(
    () =>
      allSales.filter(
        (sale) => sale.status === "draft" || sale.status === "completed",
      ),
    [allSales],
  );

  const kegPresentationIds = useMemo(() => {
    const kegFormatIds = new Set(
      packagingFormats
        .filter((format) => format.format_type === "keg")
        .map((format) => format.id),
    );

    return new Set(
      presentations
        .filter((presentation) =>
          kegFormatIds.has(presentation.packaging_format_id),
        )
        .map((presentation) => presentation.id),
    );
  }, [packagingFormats, presentations]);

  const kegLines = useMemo(
    () =>
      lines.filter((line) =>
        kegPresentationIds.has(line.beerPresentationId),
      ),
    [kegPresentationIds, lines],
  );

  const requiredKegQuantity = useMemo(
    () => kegLines.reduce((total, line) => total + line.quantity, 0),
    [kegLines],
  );

  const compatibleFilledKegs = useMemo(
    () =>
      kegs.filter(
        (keg) =>
          keg.active &&
          keg.status === "filled" &&
          keg.beer_presentation_id !== null &&
          kegLines.some(
            (line) => line.beerPresentationId === keg.beer_presentation_id,
          ),
      ),
    [kegs, kegLines],
  );

  function getRequiredKegQuantityForPresentation(
    beerPresentationId: number,
  ): number {
    return (
      kegLines.find(
        (line) => line.beerPresentationId === beerPresentationId,
      )?.quantity ?? 0
    );
  }

  function getSelectedKegQuantityForPresentation(
    beerPresentationId: number,
  ): number {
    return selectedKegIds.filter((kegId) => {
      const keg = kegs.find((item) => item.id === kegId);

      return keg?.beer_presentation_id === beerPresentationId;
    }).length;
  }

  function toggleKegSelection(kegId: number) {
  const keg = kegs.find((item) => item.id === kegId);
  const beerPresentationId = keg?.beer_presentation_id;

  if (beerPresentationId === null || beerPresentationId === undefined) {
    return;
  }

  setSelectedKegIds((currentIds) => {
    if (currentIds.includes(kegId)) {
      return currentIds.filter((id) => id !== kegId);
    }

    const requiredQuantity = getRequiredKegQuantityForPresentation(
      beerPresentationId,
    );

    const selectedQuantity = currentIds.filter((id) => {
      const selectedKeg = kegs.find((item) => item.id === id);

      return selectedKeg?.beer_presentation_id === beerPresentationId;
    }).length;

    if (selectedQuantity >= requiredQuantity) {
      return currentIds;
    }

    return [...currentIds, kegId];
  });
}

  function addLine() {
    const selectedPresentation = presentations.find(
      (presentation) => presentation.id === Number(presentationId),
    );
    const parsedQuantity = Number(quantity);

    setError(null);
    setSuccess(null);

    if (!selectedPresentation) {
      setError("Seleccioná una presentación.");
      return;
    }

    if (!Number.isInteger(parsedQuantity) || parsedQuantity <= 0) {
      setError("La cantidad debe ser un número entero mayor a cero.");
      return;
    }

    if (!activePrice) {
      setError("La presentación seleccionada no tiene un precio activo.");
      return;
    }

    if (parsedQuantity > selectedPresentation.current_stock) {
      setError("La cantidad supera el stock disponible de la presentación.");
      return;
    }

    if (
      lines.some((line) => line.beerPresentationId === selectedPresentation.id)
    ) {
      setError("La presentación ya fue agregada a la venta.");
      return;
    }

    setLines((currentLines) => [
      ...currentLines,
      {
        beerPresentationId: selectedPresentation.id,
        beerPresentationCode: selectedPresentation.code,
        beerPresentationName: selectedPresentation.name,
        quantity: parsedQuantity,
        unitPrice: activePrice.unit_price,
      },
    ]);

    setPresentationId("");
    setQuantity("1");
  }

  function removeLine(beerPresentationId: number) {
    setLines((currentLines) =>
      currentLines.filter(
        (line) => line.beerPresentationId !== beerPresentationId,
      ),
    );
  }

  async function createDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!customerId) {
      setError("Seleccioná un cliente.");
      return;
    }

    if (lines.length === 0) {
      setError("Agregá al menos un ítem a la venta.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const sale = await apiPost<Sale>("/sales/", {
        customer_id: Number(customerId),
        notes: notes.trim() || null,
      });

      for (const line of lines) {
        await apiPost<SaleItem>("/sale-items/", {
          sale_id: sale.id,
          beer_presentation_id: line.beerPresentationId,
          quantity: line.quantity,
        });
      }

      setCreatedSale(sale);
      setSelectedKegIds([]);
      setSuccess(`El borrador ${sale.code} fue creado. Ya podés completarlo.`);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el borrador de venta.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function completeSale() {
    if (!createdSale) {
      return;
    }

    if (
      requiredKegQuantity > 0 &&
      selectedKegIds.length !== requiredKegQuantity
    ) {
      setError(
        `Seleccioná ${requiredKegQuantity} barril${
          requiredKegQuantity === 1 ? "" : "es"
        } para completar esta venta.`,
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setIsCompleting(true);

    try {
      const completedSale = await apiPost<Sale>(
        `/sales/${encodeURIComponent(createdSale.code)}/complete`,
        {
          keg_ids: selectedKegIds,
        },
      );

      setCreatedSale(completedSale);
      setSuccess(
        `La venta ${completedSale.code} fue completada correctamente.`,
      );

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo completar la venta.",
      );
    } finally {
      setIsCompleting(false);
    }
  }

  async function cancelSale(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!saleToCancelCode) {
      setError("Seleccioná una venta para cancelar.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsCancelling(true);

    try {
      const cancelledSale = await apiPost<Sale>(
        `/sales/${encodeURIComponent(saleToCancelCode)}/cancel`,
        {
          cancellation_reason: cancellationReason.trim() || null,
        },
      );

      setCreatedSale((currentSale) =>
        currentSale?.id === cancelledSale.id ? cancelledSale : currentSale,
      );
      setSaleToCancelCode("");
      setCancellationReason("");
      setSuccess(`La venta ${cancelledSale.code} fue cancelada correctamente.`);

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cancelar la venta.",
      );
    } finally {
      setIsCancelling(false);
    }
  }

  function startNewSale() {
    setLines([]);
    setCustomerId("");
    setNotes("");
    setPresentationId("");
    setQuantity("1");
    setCreatedSale(null);
    setSelectedKegIds([]);
    setError(null);
    setSuccess(null);
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Ventas</h1>
        <p>Creá pedidos, cargá sus ítems y confirmá la salida de stock.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {isLoading && <p>Cargando datos comerciales...</p>}

      {!isLoading && (
        <>
          <section className="panel sales-form-panel">
            <h2>Nueva venta</h2>

            <p className="form-help">
              El código de venta se asignará automáticamente al crear el
              borrador.
            </p>

            {createdSale ? (
              <div className="sale-result">
                <p>
                  Venta <strong>{createdSale.code}</strong> en estado{" "}
                  <strong>{createdSale.status}</strong>.
                </p>

                {createdSale.status === "draft" && requiredKegQuantity > 0 && (
                  <div className="sale-line-editor">
                    <h3>Barriles para entregar</h3>

                    <p className="form-help">
                      Seleccioná los barriles físicos llenos que se entregarán
                      al cliente.
                    </p>

                    {compatibleFilledKegs.length === 0 ? (
                      <p className="empty-state">
                        No hay barriles llenos compatibles disponibles.
                      </p>
                    ) : (
                      <div className="checkbox-list">
                        {compatibleFilledKegs.map((keg) => {
                          const isSelected = selectedKegIds.includes(keg.id);
                          const presentation = presentations.find(
                            (item) => item.id === keg.beer_presentation_id,
                          );
                          const requiredForPresentation =
                            keg.beer_presentation_id === null
                              ? 0
                              : getRequiredKegQuantityForPresentation(
                                  keg.beer_presentation_id,
                                );
                          const selectedForPresentation =
                            keg.beer_presentation_id === null
                              ? 0
                              : getSelectedKegQuantityForPresentation(
                                  keg.beer_presentation_id,
                                );

                          return (
                            <label key={keg.id} className="checkbox-option">
                              <input
                                checked={isSelected}
                                disabled={
                                  !isSelected &&
                                  selectedForPresentation >=
                                    requiredForPresentation
                                }
                                onChange={() => toggleKegSelection(keg.id)}
                                type="checkbox"
                              />

                              <span>
                                <strong>{keg.code}</strong>
                                {" · "}
                                {presentation?.name ??
                                  "Presentación desconocida"}
                                {" · "}
                                {keg.current_volume_liters} L
                                {keg.form_factor !== "standard" &&
                                  ` · ${
                                    kegFormFactorLabels[keg.form_factor]
                                  }`}
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    )}

                    <p className="form-help">
                      Seleccionados: {selectedKegIds.length} de{" "}
                      {requiredKegQuantity}.
                    </p>
                  </div>
                )}

                <div className="form-actions">
                  {createdSale.status === "draft" && (
                    <button
                      disabled={isCompleting}
                      onClick={completeSale}
                      type="button"
                    >
                      {isCompleting ? "Completando..." : "Completar venta"}
                    </button>
                  )}

                  <button
                    className="secondary-button"
                    onClick={startNewSale}
                    type="button"
                  >
                    Nueva venta
                  </button>
                </div>
              </div>
            ) : (
              <form className="sale-form" onSubmit={createDraft}>
                <div className="form-grid">
                  <label>
                    Cliente
                    <select
                      onChange={(event) => setCustomerId(event.target.value)}
                      required
                      value={customerId}
                    >
                      <option value="">Seleccioná un cliente</option>

                      {customers.map((customer) => (
                        <option key={customer.id} value={customer.id}>
                          {customer.code} · {customer.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <label>
                  Notas
                  <textarea
                    onChange={(event) => setNotes(event.target.value)}
                    placeholder="Notas opcionales de la venta."
                    rows={3}
                    value={notes}
                  />
                </label>

                <div className="sale-line-editor">
                  <h3>Agregar ítem</h3>

                  <div className="form-grid line-grid">
                    <label>
                      Presentación
                      <select
                        onChange={(event) =>
                          setPresentationId(event.target.value)
                        }
                        value={presentationId}
                      >
                        <option value="">Seleccioná una presentación</option>

                        {presentations.map((presentation) => (
                          <option key={presentation.id} value={presentation.id}>
                            {presentation.code} · {presentation.name}
                            {" · Stock: "}
                            {presentation.current_stock}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Cantidad
                      <input
                        min="1"
                        onChange={(event) => setQuantity(event.target.value)}
                        step="1"
                        type="number"
                        value={quantity}
                      />
                    </label>

                    <label>
                      Precio de lista
                      <input
                        disabled
                        type="text"
                        value={
                          isPriceLoading
                            ? "Cargando precio..."
                            : activePrice
                              ? formatCurrency(activePrice.unit_price)
                              : presentationId
                                ? "Sin precio activo"
                                : "Seleccioná una presentación"
                        }
                      />
                    </label>
                  </div>

                  <button
                    className="secondary-button"
                    disabled={!activePrice || isPriceLoading}
                    onClick={addLine}
                    type="button"
                  >
                    Agregar ítem
                  </button>
                </div>

                {lines.length > 0 && (
                  <div className="draft-lines">
                    <h3>Ítems de la venta</h3>

                    <ul>
                      {lines.map((line) => (
                        <li key={line.beerPresentationId}>
                          <span>
                            <strong>{line.beerPresentationName}</strong>
                            <small>{line.beerPresentationCode}</small>
                          </span>

                          <span>
                            {line.quantity} × {formatCurrency(line.unitPrice)}
                          </span>

                          <button
                            className="text-button"
                            onClick={() => removeLine(line.beerPresentationId)}
                            type="button"
                          >
                            Quitar
                          </button>
                        </li>
                      ))}
                    </ul>

                    <p className="draft-total">
                      Total estimado:{" "}
                      <strong>{formatCurrency(String(draftTotal))}</strong>
                    </p>
                  </div>
                )}

                <button disabled={isSaving} type="submit">
                  {isSaving ? "Creando borrador..." : "Crear borrador"}
                </button>
              </form>
            )}
          </section>

          <section className="panel sales-form-panel">
            <h2>Cancelar venta</h2>

            {cancellableSales.length === 0 ? (
              <p className="empty-state">
                No hay ventas en borrador o completadas para cancelar.
              </p>
            ) : (
              <form className="sale-form" onSubmit={cancelSale}>
                <div className="form-grid">
                  <label>
                    Venta
                    <select
                      onChange={(event) =>
                        setSaleToCancelCode(event.target.value)
                      }
                      required
                      value={saleToCancelCode}
                    >
                      <option value="">Seleccioná una venta</option>

                      {cancellableSales.map((sale) => (
                        <option key={sale.id} value={sale.code}>
                          {sale.code} ·{" "}
                          {sale.status === "draft" ? "Borrador" : "Completada"}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Motivo de cancelación
                    <input
                      onChange={(event) =>
                        setCancellationReason(event.target.value)
                      }
                      placeholder="Motivo opcional."
                      value={cancellationReason}
                    />
                  </label>
                </div>

                <button
                  className="danger-button"
                  disabled={isCancelling}
                  type="submit"
                >
                  {isCancelling ? "Cancelando..." : "Cancelar venta"}
                </button>
              </form>
            )}
          </section>

          <section className="summary-grid sales-summary">
            <article className="summary-card">
              <p>Ventas completadas</p>
              <strong>{sales.length}</strong>
            </article>

            <article className="summary-card">
              <p>Unidades vendidas</p>
              <strong>{totalUnits}</strong>
            </article>

            <article className="summary-card">
              <p>Facturación</p>
              <strong>{formatCurrency(String(totalAmount))}</strong>
            </article>
          </section>

          <section className="panel">
            <h2>Ventas completadas</h2>

            {sales.length === 0 ? (
              <p className="empty-state">Todavía no hay ventas completadas.</p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Venta</th>
                      <th>Cliente</th>
                      <th>Fecha</th>
                      <th>Unidades</th>
                      <th>Importe</th>
                    </tr>
                  </thead>

                  <tbody>
                    {sales.map((sale) => (
                      <tr key={sale.sale_id}>
                        <td>{sale.sale_code}</td>
                        <td>{sale.customer_name}</td>
                        <td>{formatDate(sale.completed_at)}</td>
                        <td>{sale.total_units}</td>
                        <td>{formatCurrency(sale.total_amount)}</td>
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

export default SalesPage;