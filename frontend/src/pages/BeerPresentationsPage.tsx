import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Beer, BeerPresentation, PackagingFormat } from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

function BeerPresentationsPage() {
  const currentUser = useCurrentUser();

  const canManageCatalog = hasRole(currentUser, "admin");
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [beers, setBeers] = useState<Beer[]>([]);
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [beerId, setBeerId] = useState("");
  const [formatId, setFormatId] = useState("");
  const [minimumStock, setMinimumStock] = useState("0");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [presentationsData, beersData, formatsData] = await Promise.all([
        apiGet<BeerPresentation[]>("/beer-presentations/"),
        apiGet<Beer[]>("/beers/"),
        apiGet<PackagingFormat[]>("/packaging-formats/"),
      ]);

      setPresentations(presentationsData);
      setBeers(beersData);
      setFormats(formatsData);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar las presentaciones.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function createPresentation(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const stock = Number(minimumStock);

    if (!code.trim() || !name.trim() || !beerId || !formatId) {
      setError("Completá código, nombre, cerveza y formato.");
      return;
    }

    if (!Number.isInteger(stock) || stock < 0) {
      setError("El stock mínimo debe ser un entero igual o mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const presentation = await apiPost<BeerPresentation>(
        "/beer-presentations/",
        {
          code: code.trim(),
          name: name.trim(),
          beer_id: Number(beerId),
          packaging_format_id: Number(formatId),
          minimum_stock: stock,
          description: description.trim() || null,
        },
      );

      setCode("");
      setName("");
      setBeerId("");
      setFormatId("");
      setMinimumStock("0");
      setDescription("");
      setSuccess(
        `La presentación ${presentation.name} fue creada correctamente.`,
      );

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear la presentación.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  const beerName = (beerIdValue: number) =>
    beers.find((beer) => beer.id === beerIdValue)?.name ?? "—";

  const formatName = (formatIdValue: number) =>
    formats.find((format) => format.id === formatIdValue)?.name ?? "—";

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Presentaciones</h1>
        <p>Vinculá cervezas y formatos para gestionar el producto terminado.</p>
      </section>

      {isLoading && <p>Cargando presentaciones...</p>}
      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}
      {success && <p className="success-message">{success}</p>}

      {!isLoading && hasLoaded && (
        <>
          {canManageCatalog ? (
            <section className="panel sales-form-panel">
              <h2>Nueva presentación</h2>

              <form className="sale-form" onSubmit={createPresentation}>
                <div className="form-grid">
                  <label>
                    Código
                    <input
                      maxLength={30}
                      onChange={(event) => setCode(event.target.value)}
                      placeholder="IPA-BOT-500"
                      required
                      value={code}
                    />
                  </label>

                  <label>
                    Nombre
                    <input
                      maxLength={150}
                      onChange={(event) => setName(event.target.value)}
                      placeholder="IPA botella 500 mL"
                      required
                      value={name}
                    />
                  </label>
                </div>

                <div className="form-grid">
                  <label>
                    Cerveza
                    <select
                      onChange={(event) => setBeerId(event.target.value)}
                      required
                      value={beerId}
                    >
                      <option value="">Seleccioná una cerveza</option>
                      {beers.map((beer) => (
                        <option key={beer.id} value={beer.id}>
                          {beer.code} · {beer.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Formato
                    <select
                      onChange={(event) => setFormatId(event.target.value)}
                      required
                      value={formatId}
                    >
                      <option value="">Seleccioná un formato</option>
                      {formats.map((format) => (
                        <option key={format.id} value={format.id}>
                          {format.code} · {format.name}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="form-grid">
                  <label>
                    Stock mínimo
                    <input
                      min="0"
                      onChange={(event) => setMinimumStock(event.target.value)}
                      required
                      step="1"
                      type="number"
                      value={minimumStock}
                    />
                  </label>

                  <label>
                    Descripción
                    <input
                      onChange={(event) => setDescription(event.target.value)}
                      placeholder="Descripción opcional."
                      value={description}
                    />
                  </label>
                </div>

                <button disabled={isSaving} type="submit">
                  {isSaving ? "Creando presentación..." : "Crear presentación"}
                </button>
              </form>
            </section>
          ) : (
            <section className="panel">
              <p className="empty-state">
                Solo los administradores pueden crear presentaciones.
              </p>
            </section>
          )}

          <section className="panel">
            <h2>Presentaciones registradas</h2>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Presentación</th>
                    <th>Cerveza</th>
                    <th>Formato</th>
                    <th>Stock</th>
                    <th>Mínimo</th>
                  </tr>
                </thead>
                <tbody>
                  {presentations.map((presentation) => (
                    <tr key={presentation.id}>
                      <td>{presentation.code}</td>
                      <td>{presentation.name}</td>
                      <td>{beerName(presentation.beer_id)}</td>
                      <td>{formatName(presentation.packaging_format_id)}</td>
                      <td>{presentation.current_stock}</td>
                      <td>{presentation.minimum_stock}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </main>
  );
}

export default BeerPresentationsPage;
