import { useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet } from "../lib/api";
import type { CompletedSaleReportItem } from "../types/api";

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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSales() {
      try {
        const data = await apiGet<CompletedSaleReportItem[]>(
          "/sales/report",
        );
        setSales(data);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudieron cargar las ventas.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadSales();
  }, []);

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

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Ventas</h1>
        <p>Consultá las ventas completadas y su facturación acumulada.</p>
      </section>

      {isLoading && <p>Cargando ventas...</p>}

      {error && (
        <p className="error-message" role="alert">
          Error al cargar las ventas: {error}
        </p>
      )}

      {!isLoading && !error && (
        <>
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