import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Unit } from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

function UnitsPage() {
  const currentUser = useCurrentUser();

  const canManageCatalog =
  hasRole(currentUser, "admin") ||
  hasRole(currentUser, "operator");
  const [units, setUnits] = useState<Unit[]>([]);
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await apiGet<Unit[]>("/units/");
      setUnits(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar las unidades.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadUnits();
  }, [loadUnits]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim() || !symbol.trim()) {
      setError("Completá el nombre y el símbolo de la unidad.");
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      await apiPost<Unit>("/units/", {
        name: name.trim(),
        symbol: symbol.trim(),
      });

      setName("");
      setSymbol("");
      setSuccess("Unidad creada correctamente.");

      await loadUnits();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear la unidad.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Unidades de medida</h1>
        <p>Definí cómo se miden los insumos del inventario.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}
      {canManageCatalog ? (
        <section className="panel">
          <h2>Nueva unidad</h2>

          <form className="sale-form" onSubmit={handleSubmit}>
            <div className="form-grid">
              <label>
                Nombre
                <input
                  placeholder="Ej.: Kilogramo"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
              </label>

              <label>
                Símbolo
                <input
                  placeholder="Ej.: kg"
                  value={symbol}
                  onChange={(event) => setSymbol(event.target.value)}
                />
              </label>
            </div>

            <button disabled={isSaving} type="submit">
              {isSaving ? "Creando..." : "Crear unidad"}
            </button>
          </form>
        </section>
      ) : (
        <section className="panel">
          <p className="empty-state">
            Solo los administradores pueden modificar este catálogo.
          </p>
        </section>
      )}

      <section className="panel">
        <h2>Unidades registradas</h2>

        {isLoading ? (
          <p>Cargando unidades...</p>
        ) : units.length === 0 ? (
          <p className="empty-state">Todavía no hay unidades registradas.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Unidad</th>
                  <th>Símbolo</th>
                </tr>
              </thead>
              <tbody>
                {units.map((unit) => (
                  <tr key={unit.id}>
                    <td>{unit.name}</td>
                    <td>{unit.symbol}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default UnitsPage;
