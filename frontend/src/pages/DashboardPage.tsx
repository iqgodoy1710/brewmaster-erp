import { useEffect, useState, useMemo } from "react";

import "../App.css";
import { apiGet } from "../lib/api";
import type {
  BeerPresentationLowStock,
  CompletedSaleReportItem,
  RawMaterialLowStock,
  KegFinishedProductStock,
  PackagedFinishedProductStock,
  DeliveryOrder,
} from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

const formatCurrency = (amount: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
    currencyDisplay: "narrowSymbol",
  }).format(Number(amount));

const formatQuantity = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

function DashboardPage() {
  const currentUser = useCurrentUser();

  const canViewSales = hasRole(currentUser, "admin", "management");
  const [rawMaterialAlerts, setRawMaterialAlerts] = useState<
    RawMaterialLowStock[]
  >([]);
  const [beerPresentationAlerts, setBeerPresentationAlerts] = useState<
    BeerPresentationLowStock[]
  >([]);
  const [kegStock, setKegStock] = useState<KegFinishedProductStock[]>([]);
  const [packagedStock, setPackagedStock] = useState<
    PackagedFinishedProductStock[]
  >([]);
  const [completedSales, setCompletedSales] = useState<
    CompletedSaleReportItem[]
  >([]);
  const [deliveryOrders, setDeliveryOrders] = useState<DeliveryOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          rawMaterialData,
          beerPresentationData,
          kegStockData,
          packagedStockData,
          deliveryOrdersData,
        ] = await Promise.all([
          apiGet<RawMaterialLowStock[]>("/raw-materials/low-stock"),
          apiGet<BeerPresentationLowStock[]>("/beer-presentations/low-stock"),
          apiGet<KegFinishedProductStock[]>("/finished-product-stock/kegs"),
          apiGet<PackagedFinishedProductStock[]>(
            "/finished-product-stock/packaged",
          ),
          apiGet<DeliveryOrder[]>("/delivery-orders/"),
        ]);

        const completedSalesData = canViewSales
          ? await apiGet<CompletedSaleReportItem[]>("/sales/report")
          : [];

        setRawMaterialAlerts(rawMaterialData);
        setBeerPresentationAlerts(beerPresentationData);
        setCompletedSales(completedSalesData);
        setKegStock(kegStockData);
        setPackagedStock(packagedStockData);
        setDeliveryOrders(deliveryOrdersData);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudo cargar el dashboard.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [canViewSales]);

  const pendingDeliveryOrders = deliveryOrders.filter(
    (order) =>
      order.status === "draft" ||
      order.status === "picking" ||
      order.status === "delivered_pending_pricing",
  );

  const deliveryOrderStatusLabels = {
    draft: "Borrador",
    picking: "En preparación",
    delivered_pending_pricing: "Pendiente de precios",
    closed: "Cerrado",
    cancelled: "Cancelado",
  };
  const kegStockGroups = useMemo(() => {
    const groups = new Map<number, KegFinishedProductStock[]>();

    kegStock.forEach((item) => {
      const currentItems = groups.get(item.beer_id) ?? [];
      currentItems.push(item);
      groups.set(item.beer_id, currentItems);
    });

    return Array.from(groups.entries())
      .map(([beerId, items]) => ({
        beerId,
        beerName: items[0]?.beer_name ?? "Cerveza",
        totalKegs: items.reduce((total, item) => total + item.keg_count, 0),
        totalVolume: items.reduce(
          (total, item) => total + Number(item.total_volume_liters),
          0,
        ),
        items,
      }))
      .sort((first, second) => first.beerName.localeCompare(second.beerName));
  }, [kegStock]);

  const packagedStockGroups = useMemo(() => {
    const groups = new Map<string, PackagedFinishedProductStock[]>();

    packagedStock.forEach((item) => {
      const currentItems = groups.get(item.beer_name) ?? [];
      currentItems.push(item);
      groups.set(item.beer_name, currentItems);
    });

    return Array.from(groups.entries())
      .map(([beerName, items]) => ({
        beerName,
        totalUnits: items.reduce(
          (total, item) => total + item.current_stock,
          0,
        ),
        totalVolume: items.reduce(
          (total, item) => total + Number(item.total_volume_liters),
          0,
        ),
        items,
      }))
      .sort((first, second) => first.beerName.localeCompare(second.beerName));
  }, [packagedStock]);

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Resumen</p>
        <h1>Estado de la operación</h1>
        <p>Controlá las alertas de inventario y las ventas completadas.</p>
      </section>

      {isLoading && <p>Cargando información del dashboard...</p>}

      {error && (
        <p className="error-message" role="alert">
          Error al cargar el dashboard: {error}
        </p>
      )}

      {!isLoading && !error && (
        <>
          <section className="summary-grid" aria-label="Resumen operativo">
            <article className="summary-card">
              <p>Insumos en alerta</p>
              <strong>{rawMaterialAlerts.length}</strong>
            </article>

            <article className="summary-card">
              <p>Productos terminados en alerta</p>
              <strong>{beerPresentationAlerts.length}</strong>
            </article>

            <article className="summary-card">
              <p>Pedidos pendientes</p>
              <strong>{pendingDeliveryOrders.length}</strong>
            </article>

            {canViewSales && (
              <article className="summary-card">
                <p>Ventas completadas</p>
                <strong>{completedSales.length}</strong>
              </article>
            )}
          </section>

          <section className="dashboard-grid">
            <article className="panel">
              <h2>Alertas de insumos</h2>

              {rawMaterialAlerts.length === 0 ? (
                <p className="empty-state">
                  No hay insumos en o bajo su stock mínimo.
                </p>
              ) : (
                <ul className="alert-list">
                  {rawMaterialAlerts.map((alert) => (
                    <li key={alert.raw_material_id}>
                      <div>
                        <strong>{alert.raw_material_name}</strong>
                        <span>
                          {alert.raw_material_code} · {alert.unit_symbol}
                        </span>
                      </div>
                      <span className="shortage">
                        Faltan {formatQuantity(alert.shortage_quantity)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </article>

            <section className="panel">
              <h2>Pedidos pendientes de gestión</h2>

              {pendingDeliveryOrders.length === 0 ? (
                <p className="empty-state">
                  No hay pedidos pendientes de preparación, entrega o precios.
                </p>
              ) : (
                <ul className="alert-list">
                  {pendingDeliveryOrders.map((order) => (
                    <li key={order.id}>
                      <div>
                        <strong>{order.code}</strong>
                        <span>
                          {order.delivery_note_code
                            ? `Remito ${order.delivery_note_code}`
                            : "Sin remito emitido"}
                        </span>
                      </div>

                      <span className="shortage">
                        {deliveryOrderStatusLabels[order.status]}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <article className="panel">
              <h2>Alertas de producto terminado</h2>

              {beerPresentationAlerts.length === 0 ? (
                <p className="empty-state">
                  No hay presentaciones en o bajo su stock mínimo.
                </p>
              ) : (
                <ul className="alert-list">
                  {beerPresentationAlerts.map((alert) => (
                    <li key={alert.beer_presentation_id}>
                      <div>
                        <strong>{alert.beer_presentation_name}</strong>
                        <span>{alert.beer_presentation_code}</span>
                      </div>
                      <span className="shortage">
                        Faltan {alert.shortage_quantity} unidades
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </article>
          </section>
          <section className="dashboard-grid">
            <article className="panel">
              <h2>Stock de producto terminado · Barriles</h2>

              {kegStockGroups.length === 0 ? (
                <p className="empty-state">
                  No hay barriles llenos disponibles en fábrica.
                </p>
              ) : (
                <div className="stock-groups">
                  {kegStockGroups.map((group) => (
                    <details className="stock-group" key={group.beerId}>
                      <summary>
                        <strong>{group.beerName}</strong>

                        <span>
                          {group.totalKegs} barriles ·{" "}
                          {formatQuantity(String(group.totalVolume))} L
                        </span>
                      </summary>

                      <div className="table-wrapper">
                        <table>
                          <thead>
                            <tr>
                              <th>Formato</th>
                              <th>Variante</th>
                              <th>Barriles</th>
                              <th>Litros</th>
                            </tr>
                          </thead>

                          <tbody>
                            {group.items.map((item) => (
                              <tr
                                key={`${item.packaging_format_id}-${item.form_factor}`}
                              >
                                <td>{item.packaging_format_name}</td>
                                <td>
                                  {
                                    {
                                      standard: "Estándar",
                                      flat: "Flat",
                                      slim: "Slim",
                                    }[item.form_factor]
                                  }
                                </td>
                                <td>{item.keg_count}</td>
                                <td>
                                  {formatQuantity(item.total_volume_liters)} L
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </details>
                  ))}
                </div>
              )}
            </article>

                        <article className="panel">
              <h2>
                Stock de producto terminado · Botellas
              </h2>

              {packagedStockGroups.length === 0 ? (
                <p className="empty-state">
                  No hay botellas disponibles.
                </p>
              ) : (
                <div className="stock-groups">
                  {packagedStockGroups.map((group) => (
                    <details
                      className="stock-group"
                      key={group.beerName}
                    >
                      <summary>
                        <strong>{group.beerName}</strong>

                        <span>
                          {group.totalUnits} unidades ·{" "}
                          {formatQuantity(
                            String(group.totalVolume),
                          )}{" "}
                          L
                        </span>
                      </summary>

                      <div className="table-wrapper">
                        <table>
                          <thead>
                            <tr>
                              <th>Presentación</th>
                              <th>Formato</th>
                              <th>Unidades</th>
                              <th>Litros</th>
                            </tr>
                          </thead>

                          <tbody>
                            {group.items.map((item) => (
                              <tr key={item.beer_presentation_id}>
                                <td>
                                  {item.beer_presentation_name}
                                </td>
                                <td>
                                  {item.packaging_format_name}
                                </td>
                                <td>{item.current_stock}</td>
                                <td>
                                  {formatQuantity(
                                    item.total_volume_liters,
                                  )}{" "}
                                  L
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </details>
                  ))}
                </div>
              )}
            </article>
          </section>
          {canViewSales && (
            <section className="panel sales-panel">
              <h2>Ventas completadas</h2>

              {completedSales.length === 0 ? (
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
                      {completedSales.map((sale) => (
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
          )}
        </>
      )}
    </main>
  );
}

export default DashboardPage;
