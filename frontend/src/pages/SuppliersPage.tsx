import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Supplier } from "../types/api";

function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [name, setName] = useState("");
  const [taxId, setTaxId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadSuppliers = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await apiGet<Supplier[]>("/suppliers/");
      setSuppliers(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los proveedores.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadSuppliers();
  }, [loadSuppliers]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim() || !taxId.trim()) {
      setError("Completá el nombre y la identificación fiscal.");
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      await apiPost<Supplier>("/suppliers/", {
        name: name.trim(),
        tax_id: taxId.trim(),
      });

      setName("");
      setTaxId("");
      setSuccess("Proveedor creado correctamente.");

      await loadSuppliers();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el proveedor.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Compras</p>
        <h1>Proveedores</h1>
        <p>Registrá y consultá los proveedores de tus insumos.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      <section className="panel">
        <h2>Nuevo proveedor</h2>

        <form className="sale-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Nombre
              <input
                placeholder="Nombre o razón social"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>

            <label>
              Identificación fiscal
              <input
                placeholder="CUIT, NIF u otro identificador"
                value={taxId}
                onChange={(event) => setTaxId(event.target.value)}
              />
            </label>
          </div>

          <button disabled={isSaving} type="submit">
            {isSaving ? "Creando..." : "Crear proveedor"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>Proveedores registrados</h2>

        {isLoading ? (
          <p>Cargando proveedores...</p>
        ) : suppliers.length === 0 ? (
          <p className="empty-state">
            Todavía no hay proveedores registrados.
          </p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Proveedor</th>
                  <th>Identificación fiscal</th>
                </tr>
              </thead>
              <tbody>
                {suppliers.map((supplier) => (
                  <tr key={supplier.id}>
                    <td>{supplier.name}</td>
                    <td>{supplier.tax_id}</td>
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

export default SuppliersPage;