import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Customer } from "../types/api";

function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [name, setName] = useState("");
  const [taxId, setTaxId] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadCustomers = useCallback(async () => {
    try {
      const data = await apiGet<Customer[]>("/customers/");
      setCustomers(data);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los clientes.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCustomers();
  }, [loadCustomers]);

  async function createCustomer(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim()) {
      setError("Ingresá el nombre del cliente.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const customer = await apiPost<Customer>("/customers/", {
        name: name.trim(),
        tax_id: taxId.trim() || null,
        email: email.trim() || null,
        phone: phone.trim() || null,
        address: address.trim() || null,
        notes: notes.trim() || null,
      });

      setName("");
      setTaxId("");
      setEmail("");
      setPhone("");
      setAddress("");
      setNotes("");
      setSuccess(`El cliente ${customer.name} fue creado correctamente.`);

      await loadCustomers();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el cliente.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Clientes</h1>
        <p>Registrá y consultá los clientes disponibles para tus ventas.</p>
      </section>

      {isLoading && <p>Cargando clientes...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {!isLoading && hasLoaded && (
        <>
          <section className="panel sales-form-panel">
            <h2>Nuevo cliente</h2>

            <form className="sale-form" onSubmit={createCustomer}>
              <p className="form-help">
                El código del cliente se asignará automáticamente al guardarlo.
              </p>

              <label>
                Nombre
                <input
                  maxLength={150}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Nombre o razón social"
                  required
                  value={name}
                />
              </label>

              <div className="form-grid">
                <label>
                  Identificación fiscal
                  <input
                    maxLength={30}
                    onChange={(event) => setTaxId(event.target.value)}
                    value={taxId}
                  />
                </label>

                <label>
                  Correo electrónico
                  <input
                    maxLength={100}
                    onChange={(event) => setEmail(event.target.value)}
                    type="email"
                    value={email}
                  />
                </label>
              </div>

              <div className="form-grid">
                <label>
                  Teléfono
                  <input
                    maxLength={30}
                    onChange={(event) => setPhone(event.target.value)}
                    value={phone}
                  />
                </label>

                <label>
                  Dirección
                  <input
                    onChange={(event) => setAddress(event.target.value)}
                    value={address}
                  />
                </label>
              </div>

              <label>
                Notas
                <input
                  onChange={(event) => setNotes(event.target.value)}
                  value={notes}
                />
              </label>

              <button disabled={isSaving} type="submit">
                {isSaving ? "Creando cliente..." : "Crear cliente"}
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>Clientes registrados</h2>

            {customers.length === 0 ? (
              <p className="empty-state">
                Todavía no hay clientes registrados.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Cliente</th>
                      <th>Identificación fiscal</th>
                      <th>Correo</th>
                      <th>Teléfono</th>
                    </tr>
                  </thead>
                  <tbody>
                    {customers.map((customer) => (
                      <tr key={customer.id}>
                        <td>{customer.code}</td>
                        <td>{customer.name}</td>
                        <td>{customer.tax_id ?? "—"}</td>
                        <td>{customer.email ?? "—"}</td>
                        <td>{customer.phone ?? "—"}</td>
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

export default CustomersPage;
