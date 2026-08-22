import { useCallback, useEffect, useState, type FormEvent } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { BeerPresentation, BeerPresentationPrice } from "../types/api";
import { useSearchParams } from "react-router-dom";

const formatCurrency = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
    currencyDisplay: "narrowSymbol",
  }).format(Number(value));

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("es-ES", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

function PricesPage() {
  const [searchParams] = useSearchParams();

  const initialPresentationId = searchParams.get("presentation_id") ?? "";

  const initialUnitPrice = searchParams.get("unit_price") ?? "";
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [selectedPresentationId, setSelectedPresentationId] = useState(initialPresentationId);
  const [prices, setPrices] = useState<BeerPresentationPrice[]>([]);
  const [unitPrice, setUnitPrice] = useState(initialUnitPrice);
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadPrices = useCallback(async (beerPresentationId: string) => {
    const data = await apiGet<BeerPresentationPrice[]>(
      `/beer-presentations/${beerPresentationId}/prices`,
    );

    setPrices(data);
  }, []);

  useEffect(() => {
    async function loadPresentations() {
      try {
        const data = await apiGet<BeerPresentation[]>("/beer-presentations/");

        setPresentations(data);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudieron cargar las presentaciones.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadPresentations();
  }, []);

  useEffect(() => {
    async function loadSelectedPresentationPrices() {
      if (!selectedPresentationId) {
        setPrices([]);
        return;
      }

      try {
        await loadPrices(selectedPresentationId);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudieron cargar los precios.",
        );
      }
    }

    void loadSelectedPresentationPrices();
  }, [selectedPresentationId, loadPrices]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedPresentationId) {
      setError("Seleccioná una presentación.");
      return;
    }

    if (!unitPrice || Number(unitPrice) <= 0) {
      setError("Ingresá un precio mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const price = await apiPost<BeerPresentationPrice>(
        "/beer-presentation-prices/",
        {
          beer_presentation_id: Number(selectedPresentationId),
          unit_price: unitPrice,
          notes: notes.trim() || null,
        },
      );

      setUnitPrice("");
      setNotes("");
      setSuccess(
        `El precio ${formatCurrency(
          price.unit_price,
        )} fue publicado correctamente.`,
      );

      await loadPrices(selectedPresentationId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo publicar el precio.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  const selectedPresentation = presentations.find(
    (presentation) => presentation.id === Number(selectedPresentationId),
  );

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Precios de venta</h1>
        <p>
          Publicá el precio activo de cada presentación y consultá su historial.
        </p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {isLoading ? (
        <p>Cargando presentaciones...</p>
      ) : (
        <>
          <section className="panel sales-form-panel">
            <h2>Publicar precio</h2>

            <form className="sale-form" onSubmit={handleSubmit}>
              <div className="form-grid">
                <label>
                  Presentación
                  <select
                    onChange={(event) => {
                      setSelectedPresentationId(event.target.value);
                      setError(null);
                      setSuccess(null);
                    }}
                    required
                    value={selectedPresentationId}
                  >
                    <option value="">Seleccioná una presentación</option>
                    {presentations.map((presentation) => (
                      <option key={presentation.id} value={presentation.id}>
                        {presentation.code} · {presentation.name}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Precio de lista
                  <input
                    min="0.01"
                    onChange={(event) => setUnitPrice(event.target.value)}
                    required
                    step="0.01"
                    type="number"
                    value={unitPrice}
                  />
                </label>
              </div>

              <label>
                Notas
                <input
                  onChange={(event) => setNotes(event.target.value)}
                  placeholder="Motivo o referencia del cambio de precio."
                  value={notes}
                />
              </label>

              <button disabled={isSaving} type="submit">
                {isSaving ? "Publicando..." : "Publicar precio"}
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>
              {selectedPresentation
                ? `Historial: ${selectedPresentation.name}`
                : "Historial de precios"}
            </h2>

            {!selectedPresentationId ? (
              <p className="empty-state">
                Seleccioná una presentación para consultar sus precios.
              </p>
            ) : prices.length === 0 ? (
              <p className="empty-state">
                Esta presentación todavía no tiene precios publicados.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Precio</th>
                      <th>Vigente desde</th>
                      <th>Estado</th>
                      <th>Notas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {prices.map((price) => (
                      <tr key={price.id}>
                        <td>{formatCurrency(price.unit_price)}</td>
                        <td>{formatDate(price.effective_from)}</td>
                        <td>{price.active ? "Activo" : "Histórico"}</td>
                        <td>{price.notes ?? "—"}</td>
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

export default PricesPage;
