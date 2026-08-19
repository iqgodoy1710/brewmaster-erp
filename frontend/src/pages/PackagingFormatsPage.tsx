import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { PackagingFormat } from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }).format(Number(value));

function PackagingFormatsPage() {
  const currentUser = useCurrentUser();

  const canManageCatalog = hasRole(currentUser, "admin");
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [capacityLiters, setCapacityLiters] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadFormats = useCallback(async () => {
    try {
      const data = await apiGet<PackagingFormat[]>("/packaging-formats/");
      setFormats(data);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los formatos de envasado.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFormats();
  }, [loadFormats]);

  async function createFormat(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const capacity = Number(capacityLiters);

    if (!code.trim() || !name.trim()) {
      setError("Ingresá código y nombre para el formato.");
      return;
    }

    if (!Number.isFinite(capacity) || capacity <= 0) {
      setError("La capacidad debe ser mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const format = await apiPost<PackagingFormat>("/packaging-formats/", {
        code: code.trim(),
        name: name.trim(),
        capacity_liters: capacityLiters,
        description: description.trim() || null,
      });

      setCode("");
      setName("");
      setCapacityLiters("");
      setDescription("");
      setSuccess(`El formato ${format.name} fue creado correctamente.`);

      await loadFormats();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el formato de envasado.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Formatos de envasado</h1>
        <p>Definí las capacidades de botella, lata o barril.</p>
      </section>

      {isLoading && <p>Cargando formatos de envasado...</p>}
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
              <h2>Nuevo formato</h2>

              <form className="sale-form" onSubmit={createFormat}>
                <div className="form-grid">
                  <label>
                    Código
                    <input
                      maxLength={20}
                      onChange={(event) => setCode(event.target.value)}
                      placeholder="CAN-473"
                      required
                      value={code}
                    />
                  </label>

                  <label>
                    Nombre
                    <input
                      maxLength={100}
                      onChange={(event) => setName(event.target.value)}
                      placeholder="Lata 473 mL"
                      required
                      value={name}
                    />
                  </label>
                </div>

                <div className="form-grid">
                  <label>
                    Capacidad (L)
                    <input
                      min="0.001"
                      onChange={(event) =>
                        setCapacityLiters(event.target.value)
                      }
                      required
                      step="0.001"
                      type="number"
                      value={capacityLiters}
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
                  {isSaving ? "Creando formato..." : "Crear formato"}
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
            <h2>Formatos registrados</h2>

            {formats.length === 0 ? (
              <p className="empty-state">
                Todavía no hay formatos registrados.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Formato</th>
                      <th>Capacidad</th>
                      <th>Descripción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {formats.map((format) => (
                      <tr key={format.id}>
                        <td>{format.code}</td>
                        <td>{format.name}</td>
                        <td>{formatNumber(format.capacity_liters)} L</td>
                        <td>{format.description ?? "—"}</td>
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

export default PackagingFormatsPage;
