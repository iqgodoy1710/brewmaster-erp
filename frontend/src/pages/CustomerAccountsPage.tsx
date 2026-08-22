import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  Customer,
  CustomerAccount,
  CustomerAccountMovement,
  CustomerPayment,
  CustomerPaymentMethod,
} from "../types/api";

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

const paymentMethodLabels: Record<CustomerPaymentMethod, string> = {
  cash: "Efectivo",
  bank_transfer: "Transferencia bancaria",
  card: "Tarjeta",
  other: "Otro",
};

function movementLabel(movement: CustomerAccountMovement) {
  if (movement.movement_type === "sale_charge") {
    return "Venta completada";
  }

  if (movement.movement_type === "sale_cancellation") {
    return "Anulación de venta";
  }

  return "Pago recibido";
}

function CustomerAccountsPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [account, setAccount] = useState<CustomerAccount | null>(
    null,
  );
  const [amount, setAmount] = useState("");
  const [paymentMethod, setPaymentMethod] =
    useState<CustomerPaymentMethod>("bank_transfer");
  const [reference, setReference] = useState("");
  const [notes, setNotes] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAccount, setIsLoadingAccount] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadAccount = useCallback(async (selectedCustomerId: string) => {
    setIsLoadingAccount(true);

    try {
      const data = await apiGet<CustomerAccount>(
        `/customers/${selectedCustomerId}/account`,
      );

      setAccount(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo cargar la cuenta corriente.",
      );
    } finally {
      setIsLoadingAccount(false);
    }
  }, []);

  useEffect(() => {
    async function loadCustomers() {
      try {
        const data = await apiGet<Customer[]>("/customers/");
        setCustomers(data);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudieron cargar los clientes.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadCustomers();
  }, []);

  useEffect(() => {
    if (!customerId) {
      setAccount(null);
      return;
    }

    void loadAccount(customerId);
  }, [customerId, loadAccount]);

  async function registerPayment(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!customerId) {
      setError("Seleccioná un cliente.");
      return;
    }

    if (!amount || Number(amount) <= 0) {
      setError("Ingresá un importe mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const payment = await apiPost<CustomerPayment>(
        "/customer-payments/",
        {
          customer_id: Number(customerId),
          amount,
          payment_method: paymentMethod,
          reference: reference.trim() || null,
          notes: notes.trim() || null,
        },
      );

      setAmount("");
      setPaymentMethod("bank_transfer");
      setReference("");
      setNotes("");
      setSuccess(
        `El pago ${payment.code} fue registrado correctamente.`,
      );

      await loadAccount(customerId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo registrar el pago.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  const balance = Number(account?.balance ?? "0");

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Cuentas corrientes</h1>
        <p>
          Consultá saldos de clientes y registrá pagos recibidos.
        </p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      {isLoading ? (
        <p>Cargando clientes...</p>
      ) : (
        <>
          <section className="panel sales-form-panel">
            <h2>Cliente</h2>

            <label>
              Seleccioná un cliente
              <select
                onChange={(event) => {
                  setCustomerId(event.target.value);
                  setError(null);
                  setSuccess(null);
                }}
                value={customerId}
              >
                <option value="">Seleccioná un cliente</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.code} · {customer.name}
                  </option>
                ))}
              </select>
            </label>
          </section>

          {customerId && (
            <>
              {isLoadingAccount ? (
                <p>Cargando cuenta corriente...</p>
              ) : (
                <>
                  <section className="summary-grid sales-summary">
                    <article className="summary-card">
                      <p>
                        {balance > 0
                          ? "Saldo pendiente"
                          : balance < 0
                            ? "Saldo a favor"
                            : "Saldo actual"}
                      </p>
                      <strong>
                        {formatCurrency(
                          String(Math.abs(balance)),
                        )}
                      </strong>
                    </article>
                  </section>

                  <section className="panel sales-form-panel">
                    <h2>Registrar pago</h2>

                    <form
                      className="sale-form"
                      onSubmit={registerPayment}
                    >
                      <div className="form-grid">
                        <label>
                          Importe
                          <input
                            min="0.01"
                            onChange={(event) =>
                              setAmount(event.target.value)
                            }
                            required
                            step="0.01"
                            type="number"
                            value={amount}
                          />
                        </label>

                        <label>
                          Medio de pago
                          <select
                            onChange={(event) =>
                              setPaymentMethod(
                                event.target.value as CustomerPaymentMethod,
                              )
                            }
                            value={paymentMethod}
                          >
                            {Object.entries(paymentMethodLabels).map(
                              ([value, label]) => (
                                <option key={value} value={value}>
                                  {label}
                                </option>
                              ),
                            )}
                          </select>
                        </label>

                        <label>
                          Referencia
                          <input
                            onChange={(event) =>
                              setReference(event.target.value)
                            }
                            placeholder="Transferencia, recibo, etc."
                            value={reference}
                          />
                        </label>
                      </div>

                      <label>
                        Notas
                        <textarea
                          onChange={(event) =>
                            setNotes(event.target.value)
                          }
                          placeholder="Notas opcionales del pago."
                          rows={3}
                          value={notes}
                        />
                      </label>

                      <button disabled={isSaving} type="submit">
                        {isSaving
                          ? "Registrando..."
                          : "Registrar pago"}
                      </button>
                    </form>
                  </section>

                  <section className="panel">
                    <h2>Movimientos</h2>

                    {!account ||
                    account.movements.length === 0 ? (
                      <p className="empty-state">
                        Todavía no hay movimientos para este cliente.
                      </p>
                    ) : (
                      <div className="table-wrapper">
                        <table>
                          <thead>
                            <tr>
                              <th>Fecha</th>
                              <th>Tipo</th>
                              <th>Comprobante</th>
                              <th>Debe</th>
                              <th>Haber</th>
                              <th>Referencia</th>
                            </tr>
                          </thead>
                          <tbody>
                            {account.movements.map((movement) => {
                              const isCharge =
                                movement.movement_type ===
                                "sale_charge";

                              return (
                                <tr key={movement.id}>
                                  <td>
                                    {formatDate(movement.occurred_at)}
                                  </td>
                                  <td>{movementLabel(movement)}</td>
                                  <td>
                                    {movement.sale_code ??
                                      movement.payment_code ??
                                      "—"}
                                  </td>
                                  <td>
                                    {isCharge
                                      ? formatCurrency(movement.amount)
                                      : "—"}
                                  </td>
                                  <td>
                                    {!isCharge
                                      ? formatCurrency(movement.amount)
                                      : "—"}
                                  </td>
                                  <td>
                                    {movement.reference ?? "—"}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </section>
                </>
              )}
            </>
          )}
        </>
      )}
    </main>
  );
}

export default CustomerAccountsPage;