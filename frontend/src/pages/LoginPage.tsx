import { useState } from "react";
import type { FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import "../App.css";

type LoginPageProps = {
  onLogin: (
    email: string,
    password: string,
  ) => Promise<void>;
};

function LoginPage({
  onLogin,
}: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const location = useLocation();
  const navigate = useNavigate();

  const redirectPath =
    (
      location.state as {
        from?: { pathname?: string };
      } | null
    )?.from?.pathname ?? "/";

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await onLogin(email, password);
      navigate(redirectPath, { replace: true });
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo iniciar sesión.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="panel login-panel">
        <p className="eyebrow">BrewMaster ERP</p>
        <h1>Iniciar sesión</h1>
        <p>Ingresá con tus credenciales para acceder a la operación.</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            Correo electrónico
            <input
              autoComplete="email"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </label>

          <label>
            Contraseña
            <input
              autoComplete="current-password"
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>

          {error && (
            <p className="error-message" role="alert">
              {error}
            </p>
          )}

          <button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default LoginPage;