import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet } from "../lib/api";
import type { Sale, SaleDetail } from "../types/api";

const formatCurrency = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value));

const formatDate = (value: string | null) => {
  if (!value) {
    return "—";
  }

  return new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
};

const statusLabel = {
  draft: "Borrador",
  completed: "Completada",
  cancelled: "Cancelada",
};

function SaleDetailsPage() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [saleCode, setSaleCode] = useState("");
  const [saleDetail, setSaleDetail] = useState<SaleDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSales = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await apiGet<Sale[]>("/sales/");
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
  }, []);

  useEffect(() => {
    void loadSales();
  }, [loadSales]);

  async function handleSaleChange(nextSaleCode: string) {
    setSaleCode(nextSaleCode);
    setSaleDetail(null);

    if (!nextSaleCode) {
      return;
    }

    try {
      setIsLoadingDetail(true);
      setError(null);

      const data = await apiGet<SaleDetail>(
        `/sales/${nextSaleCode}/detail`,
      );

      setSaleDetail(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cargar el detalle de la venta.",
      );
    } finally {
      setIsLoadingDetail(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Detalle de venta</h1>
        <p>Consultá los artículos, importes y estado de cada venta.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      <section className="panel">
        <label>
          Venta
          <select
            value={saleCode}
            onChange={(event) => void handleSaleChange(event.target.value)}
          >
            <option value="">Seleccioná una venta</option>
            {sales.map((sale) => (
              <option key={sale.id} value={sale.code}>
                {sale.code} · {statusLabel[sale.status]}
              </option>
            ))}
          </select>
        </label>
      </section>

      {isLoading && <p>Cargando ventas...</p>}

      {isLoadingDetail && <p>Cargando detalle...</p>}

      {saleDetail && !isLoadingDetail && (
        <>
          <section className="panel">
            <h2>{saleDetail.code}</h2>

            <div className="form-grid">
              <p>
                <strong>Cliente:</strong> {saleDetail.customer_name}
              </p>
              <p>
                <strong>Estado:</strong> {statusLabel[saleDetail.status]}
              </p>
              <p>
                <strong>Completada:</strong>{" "}
                {formatDate(saleDetail.completed_at)}
              </p>
              <p>
                <strong>Cancelada:</strong>{" "}
                {formatDate(saleDetail.cancelled_at)}
              </p>
            </div>

            {saleDetail.notes && (
              <p>
                <strong>Notas:</strong> {saleDetail.notes}
              </p>
            )}

            {saleDetail.cancellation_reason && (
              <p>
                <strong>Motivo de cancelación:</strong>{" "}
                {saleDetail.cancellation_reason}
              </p>
            )}
          </section>

          <section className="panel">
            <h2>Artículos</h2>

            {saleDetail.items.length === 0 ? (
              <p className="empty-state">
                Esta venta no tiene artículos activos.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Presentación</th>
                      <th>Cantidad</th>
                      <th>Precio unitario</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {saleDetail.items.map((item) => (
                      <tr key={item.beer_presentation_id}>
                        <td>{item.beer_presentation_code}</td>
                        <td>{item.beer_presentation_name}</td>
                        <td>{item.quantity}</td>
                        <td>{formatCurrency(item.unit_price)}</td>
                        <td>{formatCurrency(item.line_total)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <th colSpan={4}>Total de la venta</th>
                      <th>{formatCurrency(saleDetail.total_amount)}</th>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}

export default SaleDetailsPage;