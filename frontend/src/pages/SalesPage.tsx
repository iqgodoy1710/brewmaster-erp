import { useCallback, useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  BeerPresentation,
  CompletedSaleReportItem,
  Customer,
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
    currency: "EUR",
  }).format(Number(amount));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

function SalesPage() {
  const [sales, setSales] = useState<CompletedSaleReportItem[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [lines, setLines] = useState<SaleLine[]>([]);
  const [saleCode, setSaleCode] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [notes, setNotes] = useState("");
  const [presentationId, setPresentationId] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("0.00");
  const [createdSale, setCreatedSale] = useState<Sale | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [salesData, customersData, presentationsData] =
        await Promise.all([
          apiGet<CompletedSaleReportItem[]>("/sales/report"),
          apiGet<Customer[]>("/customers/"),
          apiGet<BeerPresentation[]>("/beer-presentations/"),
        ]);

      setSales(salesData);
      setCustomers(customersData);
      setPresentations(presentationsData);
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
    loadData();
  }, [loadData]);

  const totalUnits = useMemo(
    () => sales.reduce((total, sale) => total + sale.total_units, 0),
    [sales],
  );

  const totalAmount = useMemo(
    () =>
      sales.reduce(
        (total, sale) => total + Number(sale.total_amount),
        0,
      ),
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

  function addLine() {
    const selectedPresentation = presentations.find(
      (presentation) => presentation.id === Number(presentationId),
    );
    const parsedQuantity = Number(quantity);
    const parsedUnitPrice = Number(unitPrice);

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

    if (!Number.isFinite(parsedUnitPrice) || parsedUnitPrice < 0) {
      setError("El precio unitario debe ser igual o mayor a cero.");
      return;
    }

    if (parsedQuantity > selectedPresentation.current_stock) {
      setError("La cantidad supera el stock disponible de la presentación.");
      return;
    }

    if (
      lines.some(
        (line) => line.beerPresentationId === selectedPresentation.id,
      )
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
        unitPrice: parsedUnitPrice.toFixed(2),
      },
    ]);

    setPresentationId("");
    setQuantity("1");
    setUnitPrice("0.00");
  }

  function removeLine(beerPresentationId: number) {
    setLines((currentLines) =>
      currentLines.filter(
        (line) => line.beerPresentationId !== beerPresentationId,
      ),
    );
  }

  async function createDraft(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!saleCode.trim()) {
      setError("Ingresá un código para la venta.");
      return;
    }

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
        code: saleCode.trim(),
        customer_id: Number(customerId),
        notes: notes.trim() || null,
      });

      for (const line of lines) {
        await apiPost<SaleItem>("/sale-items/", {
          sale_id: sale.id,
          beer_presentation_id: line.beerPresentationId,
          quantity: line.quantity,
          unit_price: line.unitPrice,
        });
      }

      setCreatedSale(sale);
      setSuccess(
        `El borrador ${sale.code} fue creado. Ya podés completarlo.`,
      );
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

    setError(null);
    setSuccess(null);
    setIsCompleting(true);

    try {
      const completedSale = await apiPost<Sale>(
        `/sales/${encodeURIComponent(createdSale.code)}/complete`,
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

  function startNewSale() {
    setLines([]);
    setSaleCode("");
    setCustomerId("");
    setNotes("");
    setPresentationId("");
    setQuantity("1");
    setUnitPrice("0.00");
    setCreatedSale(null);
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

            {createdSale ? (
              <div className="sale-result">
                <p>
                  Venta <strong>{createdSale.code}</strong> en estado{" "}
                  <strong>{createdSale.status}</strong>.
                </p>

                <div className="form-actions">
                  {createdSale.status === "draft" && (
                    <button
                      disabled={isCompleting}
                      onClick={completeSale}
                      type="button"
                    >
                      {isCompleting
                        ? "Completando..."
                        : "Completar venta"}
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
                    Código de venta
                    <input
                      maxLength={30}
                      onChange={(event) =>
                        setSaleCode(event.target.value)
                      }
                      placeholder="SALE-001"
                      required
                      value={saleCode}
                    />
                  </label>

                  <label>
                    Cliente
                    <select
                      onChange={(event) =>
                        setCustomerId(event.target.value)
                      }
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
                        <option value="">
                          Seleccioná una presentación
                        </option>
                        {presentations.map((presentation) => (
                          <option
                            key={presentation.id}
                            value={presentation.id}
                          >
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
                      Precio unitario
                      <input
                        min="0"
                        onChange={(event) =>
                          setUnitPrice(event.target.value)
                        }
                        step="0.01"
                        type="number"
                        value={unitPrice}
                      />
                    </label>
                  </div>

                  <button
                    className="secondary-button"
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
                            {line.quantity} ×{" "}
                            {formatCurrency(line.unitPrice)}
                          </span>

                          <button
                            className="text-button"
                            onClick={() =>
                              removeLine(line.beerPresentationId)
                            }
                            type="button"
                          >
                            Quitar
                          </button>
                        </li>
                      ))}
                    </ul>

                    <p className="draft-total">
                      Total estimado:{" "}
                      <strong>
                        {formatCurrency(String(draftTotal))}
                      </strong>
                    </p>
                  </div>
                )}

                <button disabled={isSaving} type="submit">
                  {isSaving ? "Creando borrador..." : "Crear borrador"}
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
              <p className="empty-state">
                Todavía no hay ventas completadas.
              </p>
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