import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { apiGet, apiPatch, apiPost, apiDelete } from "../lib/api";
import { hasRole, useCurrentUser } from "../lib/auth";
import type {
  BeerPresentation,
  BeerPresentationPrice,
  Customer,
  DeliveryOrder,
  DeliveryOrderDetail,
  Keg,
  PackagingFormat,
} from "../types/api";

const statusLabels = {
  draft: "Borrador",
  picking: "En preparación",
  delivered_pending_pricing: "Entregado · pendiente de precios",
  closed: "Cerrado",
  cancelled: "Cancelado",
};

function DeliveryOrdersPage() {
  const user = useCurrentUser();

  const [orders, setOrders] = useState<DeliveryOrder[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [packagingFormats, setPackagingFormats] = useState<PackagingFormat[]>(
    [],
  );
  const [kegs, setKegs] = useState<Keg[]>([]);

  const [selectedOrderCode, setSelectedOrderCode] = useState("");
  const [selectedOrder, setSelectedOrder] =
    useState<DeliveryOrderDetail | null>(null);

  const [customerId, setCustomerId] = useState("");
  const [orderNotes, setOrderNotes] = useState("");

  const [presentationId, setPresentationId] = useState("");
  const [requestedQuantity, setRequestedQuantity] = useState("1");

  const [selectedKegId, setSelectedKegId] = useState("");
  const [pricesByItemId, setPricesByItemId] = useState<Record<number, string>>(
    {},
  );

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const canCloseOrders = hasRole(user, "admin", "management");

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

  const compatibleFilledKegs = useMemo(() => {
    if (!selectedOrder) {
      return [];
    }

    const presentationIds = new Set(
      selectedOrder.items.map((item) => item.beer_presentation_id),
    );

    const assignedKegIds = new Set(
      selectedOrder.kegs.map((item) => item.keg_id),
    );

    return kegs.filter(
      (keg) =>
        keg.active &&
        keg.status === "filled" &&
        keg.beer_presentation_id !== null &&
        presentationIds.has(keg.beer_presentation_id) &&
        !assignedKegIds.has(keg.id),
    );
  }, [kegs, selectedOrder]);

  const loadBaseData = useCallback(async () => {
    try {
      const [
        ordersData,
        customersData,
        presentationsData,
        packagingFormatsData,
        kegsData,
      ] = await Promise.all([
        apiGet<DeliveryOrder[]>("/delivery-orders/"),
        apiGet<Customer[]>("/customers/"),
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
        apiGet<Keg[]>("/kegs/"),
      ]);

      setOrders(ordersData);
      setCustomers(customersData);
      setPresentations(presentationsData);
      setPackagingFormats(packagingFormatsData);
      setKegs(kegsData);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los pedidos.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadOrderDetail = useCallback(async (code: string) => {
    if (!code) {
      setSelectedOrder(null);
      return;
    }

    setIsLoadingDetail(true);

    try {
      const order = await apiGet<DeliveryOrderDetail>(
        `/delivery-orders/${encodeURIComponent(code)}`,
      );

      setSelectedOrder(order);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cargar el detalle del pedido.",
      );
    } finally {
      setIsLoadingDetail(false);
    }
  }, []);

  useEffect(() => {
    void loadBaseData();
  }, [loadBaseData]);

  useEffect(() => {
    void loadOrderDetail(selectedOrderCode);
  }, [loadOrderDetail, selectedOrderCode]);

  useEffect(() => {
    async function loadPrices() {
      if (
        !selectedOrder ||
        selectedOrder.status !== "delivered_pending_pricing"
      ) {
        setPricesByItemId({});
        return;
      }

      try {
        const prices = await Promise.all(
          selectedOrder.items.map(async (item) => {
            const presentationPrices = await apiGet<BeerPresentationPrice[]>(
              `/beer-presentations/${item.beer_presentation_id}/prices`,
            );

            return {
              itemId: item.id,
              price:
                presentationPrices.find((itemPrice) => itemPrice.active)
                  ?.unit_price ?? "",
            };
          }),
        );

        setPricesByItemId(
          Object.fromEntries(
            prices.map((price) => [price.itemId, price.price]),
          ),
        );
      } catch {
        setPricesByItemId({});
      }
    }

    void loadPrices();
  }, [selectedOrder]);

  function getPresentationName(presentationIdToFind: number): string {
    const presentation = presentations.find(
      (item) => item.id === presentationIdToFind,
    );

    return presentation
      ? `${presentation.code} · ${presentation.name}`
      : "Presentación no encontrada";
  }

  function getCustomerName(customerIdToFind: number): string {
    return (
      customers.find((customer) => customer.id === customerIdToFind)?.name ??
      "Cliente no encontrado"
    );
  }

  function getKegName(kegId: number): string {
    return kegs.find((keg) => keg.id === kegId)?.code ?? "Barril no encontrado";
  }

  function escapeHtml(value: string): string {
    return value.replace(
      /[&<>"']/g,
      (character) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#039;",
        })[character] ?? character,
    );
  }

  function printDeliveryNote() {
    if (!selectedOrder || !selectedOrder.delivery_note_code) {
      return;
    }

    const customer = customers.find(
      (item) => item.id === selectedOrder.customer_id,
    );

    const deliveredItems = selectedOrder.items.filter(
      (item) => item.delivered_quantity > 0,
    );

    const itemRows = deliveredItems
      .map(
        (item) => `
          <tr>
            <td>${escapeHtml(
              getPresentationName(item.beer_presentation_id),
            )}</td>
            <td class="quantity">${item.delivered_quantity}</td>
          </tr>
        `,
      )
      .join("");

    const kegRows = selectedOrder.kegs
      .map(
        (item) => `
          <li>${escapeHtml(getKegName(item.keg_id))}</li>
        `,
      )
      .join("");

    const deliveredAt = selectedOrder.delivered_at
      ? new Intl.DateTimeFormat("es-AR", {
          dateStyle: "long",
          timeStyle: "short",
        }).format(new Date(selectedOrder.delivered_at))
      : "—";

    const printWindow = window.open("", "_blank");

    if (!printWindow) {
      setError(
        "El navegador bloqueó la ventana de impresión. Habilitá las ventanas emergentes e intentá nuevamente.",
      );
      return;
    }

    printWindow.document.write(`
      <!doctype html>
      <html lang="es">
        <head>
          <meta charset="utf-8" />
          <title>Remito ${escapeHtml(selectedOrder.delivery_note_code)}</title>
          <style>
            @page {
              margin: 18mm;
            }

            * {
              box-sizing: border-box;
            }

            body {
              color: #172033;
              font-family: Arial, sans-serif;
              font-size: 12px;
              margin: 0;
            }

            .header {
              align-items: flex-start;
              border-bottom: 2px solid #e5a400;
              display: flex;
              justify-content: space-between;
              padding-bottom: 16px;
            }

            .brand {
              color: #b66b00;
              font-size: 22px;
              font-weight: 800;
              letter-spacing: 0.08em;
              margin: 0;
            }

            .brand-subtitle {
              color: #52647f;
              margin: 4px 0 0;
            }

            .document-title {
              margin: 24px 0 16px;
            }

            .document-title h1 {
              font-size: 24px;
              margin: 0;
            }

            .document-title p {
              color: #52647f;
              margin: 6px 0 0;
            }

            .customer {
              background: #f6f8fc;
              border: 1px solid #d8e0ed;
              border-radius: 8px;
              display: grid;
              gap: 6px;
              margin: 18px 0;
              padding: 14px;
            }

            table {
              border-collapse: collapse;
              margin-top: 16px;
              width: 100%;
            }

            th,
            td {
              border-bottom: 1px solid #d8e0ed;
              padding: 10px 8px;
              text-align: left;
            }

            th {
              color: #52647f;
              font-size: 10px;
              text-transform: uppercase;
            }

            .quantity {
              text-align: right;
            }

            .kegs {
              margin-top: 22px;
            }

            .kegs h2 {
              font-size: 14px;
              margin-bottom: 8px;
            }

            .notes {
              margin-top: 24px;
            }

            .footer {
              border-top: 1px solid #d8e0ed;
              color: #52647f;
              margin-top: 42px;
              padding-top: 12px;
            }
          </style>
        </head>
        <body>
          <header class="header">
            <div>
              <p class="brand">ELIXIA</p>
              <p class="brand-subtitle">art beer · Remito de entrega</p>
            </div>

            <div>
              <strong>Remito ${escapeHtml(
                selectedOrder.delivery_note_code,
              )}</strong>
              <p>Pedido ${escapeHtml(selectedOrder.code)}</p>
            </div>
          </header>

          <section class="document-title">
            <h1>Remito de entrega</h1>
            <p>Fecha de entrega: ${escapeHtml(deliveredAt)}</p>
          </section>

          <section class="customer">
            <strong>Cliente: ${escapeHtml(
              customer?.name ?? "Cliente no encontrado",
            )}</strong>
            ${
              customer?.address
                ? `<span>Dirección: ${escapeHtml(customer.address)}</span>`
                : ""
            }
            ${
              customer?.phone
                ? `<span>Teléfono: ${escapeHtml(customer.phone)}</span>`
                : ""
            }
            ${
              customer?.tax_id
                ? `<span>CUIT / Identificación: ${escapeHtml(
                    customer.tax_id,
                  )}</span>`
                : ""
            }
          </section>

          <table>
            <thead>
              <tr>
                <th>Artículo entregado</th>
                <th class="quantity">Cantidad</th>
              </tr>
            </thead>
            <tbody>
              ${itemRows}
            </tbody>
          </table>

          ${
            kegRows
              ? `
                <section class="kegs">
                  <h2>Barriles entregados</h2>
                  <ul>${kegRows}</ul>
                </section>
              `
              : ""
          }

          ${
            selectedOrder.notes
              ? `
                <section class="notes">
                  <strong>Observaciones</strong>
                  <p>${escapeHtml(selectedOrder.notes)}</p>
                </section>
              `
              : ""
          }

          <footer class="footer">
            Documento generado por ELIXIA ERP.
          </footer>
        </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  }

  async function refreshOrder(code: string) {
    await Promise.all([loadBaseData(), loadOrderDetail(code)]);
  }

  async function createOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!customerId) {
      setError("Seleccioná un cliente.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const order = await apiPost<DeliveryOrder>("/delivery-orders/", {
        customer_id: Number(customerId),
        notes: orderNotes.trim() || null,
      });

      setCustomerId("");
      setOrderNotes("");
      setSelectedOrderCode(order.code);
      setSuccess(
        `El pedido ${order.code} fue creado. Ahora podés agregar sus artículos.`,
      );

      await refreshOrder(order.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el pedido.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function addItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedOrder || !presentationId) {
      setError("Seleccioná una presentación.");
      return;
    }

    const quantity = Number(requestedQuantity);

    if (!Number.isInteger(quantity) || quantity <= 0) {
      setError("La cantidad debe ser un número entero mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiPost(
        `/delivery-orders/${encodeURIComponent(selectedOrder.code)}/items`,
        {
          beer_presentation_id: Number(presentationId),
          requested_quantity: quantity,
        },
      );

      setPresentationId("");
      setRequestedQuantity("1");
      setSuccess("El artículo fue agregado al pedido.");

      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo agregar el artículo.",
      );
    } finally {
      setIsSaving(false);
    }
  }
  async function updateDraftItem(itemId: number, requestedQuantity: string) {
    if (!selectedOrder) {
      return;
    }

    const quantity = Number(requestedQuantity);

    if (!Number.isInteger(quantity) || quantity <= 0) {
      setError(
        "La cantidad solicitada debe ser un número entero mayor a cero.",
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiPatch(
        `/delivery-orders/${encodeURIComponent(
          selectedOrder.code,
        )}/items/${itemId}`,
        {
          requested_quantity: quantity,
        },
      );

      setSuccess("La cantidad solicitada fue actualizada.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo actualizar el artículo.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function removeDraftItem(itemId: number) {
    if (!selectedOrder) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiDelete(
        `/delivery-orders/${encodeURIComponent(
          selectedOrder.code,
        )}/items/${itemId}`,
      );

      setSuccess("El artículo fue quitado del pedido.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo quitar el artículo.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function removeAssignedKeg(kegId: number) {
    if (!selectedOrder) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiDelete(
        `/delivery-orders/${encodeURIComponent(
          selectedOrder.code,
        )}/kegs/${kegId}`,
      );

      setSuccess("El barril fue quitado del pedido.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo quitar el barril.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function startPicking() {
    if (!selectedOrder) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiPost(
        `/delivery-orders/${encodeURIComponent(
          selectedOrder.code,
        )}/start-picking`,
      );

      setSuccess("El pedido pasó a preparación.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo iniciar la preparación.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function updatePicking(itemId: number, pickedQuantity: string) {
    if (!selectedOrder) {
      return;
    }

    const quantity = Number(pickedQuantity);

    if (!Number.isInteger(quantity) || quantity < 0) {
      setError(
        "La cantidad preparada debe ser un número entero igual o mayor a cero.",
      );
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiPatch(
        `/delivery-orders/${encodeURIComponent(
          selectedOrder.code,
        )}/items/${itemId}/picking`,
        {
          picked_quantity: quantity,
        },
      );

      setSuccess("La cantidad preparada fue actualizada.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo actualizar el picking.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function assignKeg() {
    if (!selectedOrder || !selectedKegId) {
      setError("Seleccioná un barril lleno.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiPost(
        `/delivery-orders/${encodeURIComponent(selectedOrder.code)}/kegs`,
        {
          keg_id: Number(selectedKegId),
        },
      );

      setSelectedKegId("");
      setSuccess("El barril fue asignado al pedido.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo asignar el barril.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function deliverOrder() {
    if (!selectedOrder) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const deliveredOrder = await apiPost<DeliveryOrder>(
        `/delivery-orders/${encodeURIComponent(selectedOrder.code)}/deliver`,
        {},
      );

      setSuccess(
        `Pedido entregado. Se generó el remito ${deliveredOrder.delivery_note_code}.`,
      );
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar la entrega.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function closeOrder() {
    if (!selectedOrder) {
      return;
    }

    const deliveredItems = selectedOrder.items.filter(
      (item) => item.delivered_quantity > 0,
    );

    const items = deliveredItems.map((item) => ({
      delivery_order_item_id: item.id,
      unit_price: pricesByItemId[item.id],
    }));

    if (items.length === 0) {
      setError("El pedido no tiene artículos entregados para cerrar.");
      return;
    }

    if (
      items.some((item) => !item.unit_price || Number(item.unit_price) <= 0)
    ) {
      setError("Ingresá un precio válido para cada artículo entregado.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const sale = await apiPost<{ code: string }>(
        `/delivery-orders/${encodeURIComponent(selectedOrder.code)}/close`,
        { items },
      );

      setSuccess(
        `El pedido fue cerrado y se generó la venta ${sale.code} en la cuenta corriente.`,
      );
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cerrar el pedido.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function cancelOrder() {
    if (!selectedOrder) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      await apiPost(
        `/delivery-orders/${encodeURIComponent(selectedOrder.code)}/cancel`,
      );

      setSuccess("El pedido fue cancelado.");
      await refreshOrder(selectedOrder.code);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cancelar el pedido.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Pedidos</h1>
        <p>
          Prepará entregas, registrá el picking y cerrá los precios después de
          la entrega.
        </p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {isLoading && <p>Cargando pedidos...</p>}

      {!isLoading && (
        <>
          <section className="panel sales-form-panel">
            <h2>Nuevo pedido</h2>

            <p className="form-help">
              El código se genera automáticamente. Los precios se revisan al
              cerrar la entrega.
            </p>

            <form className="sale-form" onSubmit={createOrder}>
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
                  onChange={(event) => setOrderNotes(event.target.value)}
                  placeholder="Notas opcionales para logística."
                  rows={3}
                  value={orderNotes}
                />
              </label>

              <button disabled={isSaving} type="submit">
                {isSaving ? "Creando..." : "Crear pedido"}
              </button>
            </form>
          </section>

          <section className="panel sales-form-panel">
            <h2>Gestionar pedido</h2>

            <label>
              Pedido
              <select
                onChange={(event) => setSelectedOrderCode(event.target.value)}
                value={selectedOrderCode}
              >
                <option value="">Seleccioná un pedido</option>

                {orders.map((order) => (
                  <option key={order.id} value={order.code}>
                    {order.code} · {getCustomerName(order.customer_id)} ·{" "}
                    {statusLabels[order.status]}
                  </option>
                ))}
              </select>
            </label>

            {isLoadingDetail && <p>Cargando detalle...</p>}

            {selectedOrder && !isLoadingDetail && (
              <div className="sale-result">
                <p>
                  <strong>{selectedOrder.code}</strong>
                  {" · "}
                  {getCustomerName(selectedOrder.customer_id)}
                  {" · "}
                  <strong>{statusLabels[selectedOrder.status]}</strong>
                </p>

                {selectedOrder.delivery_note_code && (
                  <p>
                    Remito: <strong>{selectedOrder.delivery_note_code}</strong>
                  </p>
                )}

                {selectedOrder.notes && <p>Notas: {selectedOrder.notes}</p>}

                {selectedOrder.status === "draft" && (
                  <>
                    <div className="sale-line-editor">
                      <h3>Agregar artículo</h3>

                      <form className="sale-form" onSubmit={addItem}>
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
                            Cantidad solicitada
                            <input
                              min="1"
                              onChange={(event) =>
                                setRequestedQuantity(event.target.value)
                              }
                              step="1"
                              type="number"
                              value={requestedQuantity}
                            />
                          </label>
                        </div>

                        <button
                          className="secondary-button"
                          disabled={isSaving}
                          type="submit"
                        >
                          Agregar artículo
                        </button>
                      </form>
                    </div>

                    {selectedOrder.items.length > 0 && (
                      <button
                        disabled={isSaving}
                        onClick={startPicking}
                        type="button"
                      >
                        Iniciar preparación
                      </button>
                    )}
                  </>
                )}

                {selectedOrder.items.length === 0 ? (
                  <p className="empty-state">
                    Todavía no hay artículos en este pedido.
                  </p>
                ) : (
                  <div className="table-wrapper">
                    <table>
                      <thead>
                        <tr>
                          <th>Presentación</th>
                          <th>Solicitado</th>
                          <th>Preparado</th>
                          <th>Entregado</th>
                          {selectedOrder.status === "draft" && <th>Acción</th>}
                          {selectedOrder.status === "picking" && (
                            <th>Acción</th>
                          )}
                          {selectedOrder.status ===
                            "delivered_pending_pricing" && (
                            <th>Precio final</th>
                          )}
                        </tr>
                      </thead>

                      <tbody>
                        {selectedOrder.items.map((item) => (
                          <tr key={item.id}>
                            <td>
                              {getPresentationName(item.beer_presentation_id)}
                            </td>
                            <td>{item.requested_quantity}</td>
                            <td>{item.picked_quantity}</td>
                            <td>{item.delivered_quantity}</td>
                            {selectedOrder.status === "draft" && (
                              <td>
                                <div className="form-actions">
                                  <input
                                    defaultValue={item.requested_quantity}
                                    min="1"
                                    onBlur={(event) =>
                                      void updateDraftItem(
                                        item.id,
                                        event.target.value,
                                      )
                                    }
                                    step="1"
                                    type="number"
                                  />

                                  <button
                                    className="danger-button"
                                    disabled={isSaving}
                                    onClick={() =>
                                      void removeDraftItem(item.id)
                                    }
                                    type="button"
                                  >
                                    Quitar
                                  </button>
                                </div>
                              </td>
                            )}

                            {selectedOrder.status === "picking" && (
                              <td>
                                <div className="form-actions">
                                  <input
                                    defaultValue={item.picked_quantity}
                                    min="0"
                                    onBlur={(event) =>
                                      void updatePicking(
                                        item.id,
                                        event.target.value,
                                      )
                                    }
                                    step="1"
                                    type="number"
                                  />
                                </div>
                              </td>
                            )}

                            {selectedOrder.status ===
                              "delivered_pending_pricing" && (
                              <td>
                                {item.delivered_quantity > 0 ? (
                                  <input
                                    min="0.01"
                                    onChange={(event) =>
                                      setPricesByItemId((currentPrices) => ({
                                        ...currentPrices,
                                        [item.id]: event.target.value,
                                      }))
                                    }
                                    step="0.01"
                                    type="number"
                                    value={pricesByItemId[item.id] ?? ""}
                                  />
                                ) : (
                                  "—"
                                )}
                              </td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {selectedOrder.status === "picking" &&
                  selectedOrder.items.some((item) =>
                    kegPresentationIds.has(item.beer_presentation_id),
                  ) && (
                    <div className="sale-line-editor">
                      <h3>Barriles físicos para entregar</h3>

                      <p className="form-help">
                        Asigná un barril lleno por cada unidad de presentación
                        tipo barril preparada.
                      </p>

                      <div className="form-grid">
                        <label>
                          Barril lleno
                          <select
                            onChange={(event) =>
                              setSelectedKegId(event.target.value)
                            }
                            value={selectedKegId}
                          >
                            <option value="">Seleccioná un barril</option>

                            {compatibleFilledKegs.map((keg) => (
                              <option key={keg.id} value={keg.id}>
                                {keg.code} ·{" "}
                                {getPresentationName(
                                  keg.beer_presentation_id ?? 0,
                                )}{" "}
                                · {keg.current_volume_liters} L
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>

                      <button
                        className="secondary-button"
                        disabled={isSaving || !selectedKegId}
                        onClick={assignKeg}
                        type="button"
                      >
                        Asignar barril
                      </button>

                      {selectedOrder.kegs.length > 0 && (
                        <ul>
                          {selectedOrder.kegs.map((item) => (
                            <li key={item.id}>
                              {getKegName(item.keg_id)}

                              <button
                                className="text-button"
                                disabled={isSaving}
                                onClick={() =>
                                  void removeAssignedKeg(item.keg_id)
                                }
                                type="button"
                              >
                                Quitar
                              </button>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}

                <div className="form-actions">
                  {selectedOrder.status === "picking" && (
                    <button
                      disabled={isSaving}
                      onClick={deliverOrder}
                      type="button"
                    >
                      Registrar entrega y emitir remito
                    </button>
                  )}

                  {selectedOrder.status === "delivered_pending_pricing" &&
                    canCloseOrders && (
                      <button
                        disabled={isSaving}
                        onClick={closeOrder}
                        type="button"
                      >
                        Cerrar pedido y generar venta
                      </button>
                    )}
                  {selectedOrder.delivery_note_code && (
                    <button
                      className="secondary-button"
                      onClick={printDeliveryNote}
                      type="button"
                    >
                      Imprimir remito
                    </button>
                  )}

                  {(selectedOrder.status === "draft" ||
                    selectedOrder.status === "picking") && (
                    <button
                      className="danger-button"
                      disabled={isSaving}
                      onClick={cancelOrder}
                      type="button"
                    >
                      Cancelar pedido
                    </button>
                  )}
                </div>
              </div>
            )}
          </section>

          <section className="panel">
            <h2>Pedidos registrados</h2>

            {orders.length === 0 ? (
              <p className="empty-state">Todavía no hay pedidos creados.</p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Pedido</th>
                      <th>Cliente</th>
                      <th>Estado</th>
                      <th>Remito</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((order) => (
                      <tr key={order.id}>
                        <td>{order.code}</td>
                        <td>{getCustomerName(order.customer_id)}</td>
                        <td>{statusLabels[order.status]}</td>
                        <td>{order.delivery_note_code ?? "—"}</td>
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

export default DeliveryOrdersPage;
