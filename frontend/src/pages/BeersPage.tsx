import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Beer } from "../types/api";

function BeersPage() {
  const [beers, setBeers] = useState<Beer[]>([]);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [style, setStyle] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadBeers = useCallback(async () => {
    try {
      const data = await apiGet<Beer[]>("/beers/");
      setBeers(data);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar las cervezas.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBeers();
  }, [loadBeers]);

  async function createBeer(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!code.trim()) {
      setError("Ingresá un código para la cerveza.");
      return;
    }

    if (!name.trim()) {
      setError("Ingresá el nombre de la cerveza.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const beer = await apiPost<Beer>("/beers/", {
        code: code.trim(),
        name: name.trim(),
        style: style.trim() || null,
        description: description.trim() || null,
      });

      setCode("");
      setName("");
      setStyle("");
      setDescription("");
      setSuccess(`La cerveza ${beer.name} fue creada correctamente.`);

      await loadBeers();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear la cerveza.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Cervezas</h1>
        <p>Registrá las cervezas base para recetas y presentaciones.</p>
      </section>

      {isLoading && <p>Cargando cervezas...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {!isLoading && hasLoaded && (
        <>
          <section className="panel sales-form-panel">
            <h2>Nueva cerveza</h2>

            <form className="sale-form" onSubmit={createBeer}>
              <div className="form-grid">
                <label>
                  Código
                  <input
                    maxLength={20}
                    onChange={(event) => setCode(event.target.value)}
                    placeholder="IPA-001"
                    required
                    value={code}
                  />
                </label>

                <label>
                  Nombre
                  <input
                    maxLength={100}
                    onChange={(event) => setName(event.target.value)}
                    placeholder="IPA clásica"
                    required
                    value={name}
                  />
                </label>
              </div>

              <div className="form-grid">
                <label>
                  Estilo
                  <input
                    maxLength={50}
                    onChange={(event) => setStyle(event.target.value)}
                    placeholder="India Pale Ale"
                    value={style}
                  />
                </label>

                <label>
                  Descripción
                  <input
                    onChange={(event) =>
                      setDescription(event.target.value)
                    }
                    placeholder="Descripción opcional."
                    value={description}
                  />
                </label>
              </div>

              <button disabled={isSaving} type="submit">
                {isSaving ? "Creando cerveza..." : "Crear cerveza"}
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>Cervezas registradas</h2>

            {beers.length === 0 ? (
              <p className="empty-state">
                Todavía no hay cervezas registradas.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Cerveza</th>
                      <th>Estilo</th>
                      <th>Descripción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {beers.map((beer) => (
                      <tr key={beer.id}>
                        <td>{beer.code}</td>
                        <td>{beer.name}</td>
                        <td>{beer.style ?? "—"}</td>
                        <td>{beer.description ?? "—"}</td>
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

export default BeersPage;