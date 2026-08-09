import { useEffect, useState } from "react";

import "../App.css";
import { apiGet } from "../lib/api";
import type { RawMaterial } from "../types/api";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }).format(Number(value));

const formatCurrency = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value));

function RawMaterialsPage() {
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRawMaterials() {
      try {
        const data = await apiGet<RawMaterial[]>("/raw-materials/");
        setRawMaterials(data);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudieron cargar los insumos.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadRawMaterials();
  }, []);

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Inventario</p>
        <h1>Insumos</h1>
        <p>Consultá el stock, mínimo configurado y costo actual.</p>
      </section>

      {isLoading && <p>Cargando insumos...</p>}

      {error && (
        <p className="error-message" role="alert">
          Error al cargar los insumos: {error}
        </p>
      )}

      {!isLoading && !error && (
        <section className="panel">
          {rawMaterials.length === 0 ? (
            <p className="empty-state">
              Todavía no hay insumos registrados.
            </p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Insumo</th>
                    <th>Stock actual</th>
                    <th>Stock mínimo</th>
                    <th>Costo actual</th>
                  </tr>
                </thead>
                <tbody>
                  {rawMaterials.map((rawMaterial) => (
                    <tr key={rawMaterial.id}>
                      <td>{rawMaterial.code}</td>
                      <td>{rawMaterial.name}</td>
                      <td>{formatNumber(rawMaterial.current_stock)}</td>
                      <td>{formatNumber(rawMaterial.minimum_stock)}</td>
                      <td>{formatCurrency(rawMaterial.current_cost)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

export default RawMaterialsPage;