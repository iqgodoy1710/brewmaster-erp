import { useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPatch } from "../lib/api";
import type { BeerPresentation } from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

function FinishedProductsPage() {
  const currentUser = useCurrentUser();

  const canManageMinimumStock = hasRole(currentUser, "admin", "management");
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [minimumStockInputs, setMinimumStockInputs] = useState<
    Record<string, string>
  >({});
  const [isLoading, setIsLoading] = useState(true);
  const [savingCode, setSavingCode] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadPresentations() {
      try {
        const data = await apiGet<BeerPresentation[]>("/beer-presentations/");

        setPresentations(data);
        setMinimumStockInputs(
          Object.fromEntries(
            data.map((presentation) => [
              presentation.code,
              String(presentation.minimum_stock),
            ]),
          ),
        );
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudo cargar el producto terminado.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadPresentations();
  }, []);

  async function updateMinimumStock(
    event: React.FormEvent<HTMLFormElement>,
    presentation: BeerPresentation,
  ) {
    event.preventDefault();

    const value = Number(minimumStockInputs[presentation.code]);

    if (!Number.isInteger(value) || value < 0) {
      setError(
        "El stock mínimo debe ser un número entero igual o mayor a cero.",
      );
      return;
    }

    setSavingCode(presentation.code);
    setError(null);

    try {
      const updatedPresentation = await apiPatch<BeerPresentation>(
        `/beer-presentations/${encodeURIComponent(
          presentation.code,
        )}/minimum-stock`,
        {
          minimum_stock: value,
        },
      );

      setPresentations((currentPresentations) =>
        currentPresentations.map((currentPresentation) =>
          currentPresentation.id === updatedPresentation.id
            ? updatedPresentation
            : currentPresentation,
        ),
      );

      setMinimumStockInputs((currentInputs) => ({
        ...currentInputs,
        [updatedPresentation.code]: String(updatedPresentation.minimum_stock),
      }));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo actualizar el stock mínimo.",
      );
    } finally {
      setSavingCode(null);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Inventario</p>
        <h1>Producto terminado</h1>
        <p>
          Consultá el stock por presentación y configurá sus mínimos de alerta.
        </p>
      </section>

      {isLoading && <p>Cargando producto terminado...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {!isLoading && (presentations.length > 0 || !error) && (
        <section className="panel">
          {presentations.length === 0 ? (
            <p className="empty-state">
              Todavía no hay presentaciones registradas.
            </p>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Presentación</th>
                    <th>Stock actual</th>
                    <th>Stock mínimo</th>
                  </tr>
                </thead>
                <tbody>
                  {presentations.map((presentation) => (
                    <tr key={presentation.id}>
                      <td>{presentation.code}</td>
                      <td>{presentation.name}</td>
                      <td>{presentation.current_stock}</td>
                      <td>
                        {canManageMinimumStock ? (
                          <form
                            className="minimum-stock-form"
                            onSubmit={(event) =>
                              updateMinimumStock(event, presentation)
                            }
                          >
                            <input
                              aria-label={`Stock mínimo de ${presentation.name}`}
                              min="0"
                              step="1"
                              type="number"
                              value={
                                minimumStockInputs[presentation.code] ??
                                String(presentation.minimum_stock)
                              }
                              onChange={(event) =>
                                setMinimumStockInputs((currentInputs) => ({
                                  ...currentInputs,
                                  [presentation.code]: event.target.value,
                                }))
                              }
                            />
                            <button
                              disabled={savingCode === presentation.code}
                              type="submit"
                            >
                              {savingCode === presentation.code
                                ? "Guardando..."
                                : "Guardar"}
                            </button>
                          </form>
                        ) : (
                          presentation.minimum_stock
                        )}
                      </td>
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

export default FinishedProductsPage;
