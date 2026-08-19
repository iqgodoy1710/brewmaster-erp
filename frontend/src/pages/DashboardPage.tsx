import { useEffect, useState } from "react";

import "../App.css";
import { apiGet } from "../lib/api";
import type {
  BeerPresentationLowStock,
  CompletedSaleReportItem,
  RawMaterialLowStock,
} from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

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

function DashboardPage() {
  const currentUser = useCurrentUser();

  const canViewSales = hasRole(currentUser, "admin", "management");
  const [rawMaterialAlerts, setRawMaterialAlerts] = useState<
    RawMaterialLowStock[]
  >([]);
  const [beerPresentationAlerts, setBeerPresentationAlerts] = useState<
    BeerPresentationLowStock[]
  >([]);
  const [completedSales, setCompletedSales] = useState<
    CompletedSaleReportItem[]
  >([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [rawMaterialData, beerPresentationData] = await Promise.all([
          apiGet<RawMaterialLowStock[]>("/raw-materials/low-stock"),
          apiGet<BeerPresentationLowStock[]>("/beer-presentations/low-stock"),
        ]);

        const completedSalesData = canViewSales
          ? await apiGet<CompletedSaleReportItem[]>("/sales/report")
          : [];

        setRawMaterialAlerts(rawMaterialData);
        setBeerPresentationAlerts(beerPresentationData);
        setCompletedSales(completedSalesData);
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
                        Faltan {alert.shortage_quantity}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </article>

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
