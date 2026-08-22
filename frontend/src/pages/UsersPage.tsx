import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPatch, apiPost } from "../lib/api";
import { useCurrentUser } from "../lib/auth";
import type { AuthenticatedUser, UserRole } from "../types/api";

const roleLabels: Record<UserRole, string> = {
  admin: "Administrador",
  operator: "Operador",
  management: "Gerencia",
};

function UsersPage() {
  const currentUser = useCurrentUser();
  const [users, setUsers] = useState<AuthenticatedUser[]>([]);
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("operator");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [updatingUserId, setUpdatingUserId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editedUsernames, setEditedUsernames] = useState<
    Record<number, string>
  >({});

  const loadUsers = useCallback(async () => {
    try {
      const data = await apiGet<AuthenticatedUser[]>("/users/");
      setUsers(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los usuarios.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  async function createUser(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const user = await apiPost<AuthenticatedUser>("/users/", {
        username: username.trim(),
        full_name: fullName.trim(),
        password,
        role,
      });

      setUsers((currentUsers) => [...currentUsers, user]);
      setUsername("");
      setFullName("");
      setPassword("");
      setRole("operator");
      setSuccess(`El usuario ${user.full_name} fue creado.`);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear el usuario.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function updateUser(
    userId: number,
    data: {
      active?: boolean;
      role?: UserRole;
      username?: string;
    },
  ) {
    setError(null);
    setSuccess(null);
    setUpdatingUserId(userId);

    try {
      const updatedUser = await apiPatch<AuthenticatedUser>(
        `/users/${userId}`,
        data,
      );

      setUsers((currentUsers) =>
        currentUsers.map((user) =>
          user.id === updatedUser.id ? updatedUser : user,
        ),
      );
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo actualizar el usuario.",
      );
    } finally {
      setUpdatingUserId(null);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Administración</p>
        <h1>Usuarios</h1>
        <p>Gestioná las cuentas y los roles de acceso de la cervecería.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}

      <section className="panel sales-form-panel">
        <h2>Nuevo usuario</h2>

        <form className="sale-form" onSubmit={createUser}>
          <div className="form-grid">
            <label>
              Nombre completo
              <input
                onChange={(event) => setFullName(event.target.value)}
                required
                value={fullName}
              />
            </label>

            <label>
              Nombre de usuario
              <input
                onChange={(event) => setUsername(event.target.value)}
                required
                type="text"
                value={username}
                autoComplete="username"
                minLength={3}
                maxLength={50}
                pattern="[A-Za-z0-9._-]+"
              />
            </label>
          </div>

          <div className="form-grid">
            <label>
              Contraseña inicial
              <input
                minLength={8}
                onChange={(event) => setPassword(event.target.value)}
                required
                type="password"
                value={password}
              />
            </label>

            <label>
              Rol
              <select
                onChange={(event) => setRole(event.target.value as UserRole)}
                value={role}
              >
                <option value="operator">Operador</option>
                <option value="management">Gerencia</option>
                <option value="admin">Administrador</option>
              </select>
            </label>
          </div>

          <button disabled={isSaving} type="submit">
            {isSaving ? "Creando..." : "Crear usuario"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>Usuarios registrados</h2>

        {isLoading ? (
          <p>Cargando usuarios...</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => {
                  const isCurrentUser = user.id === currentUser?.id;
                  const isUpdating = updatingUserId === user.id;

                  return (
                    <tr key={user.id}>
                      <td>{user.full_name}</td>
                      <td>
                        {isCurrentUser ? (
                          user.username
                        ) : (
                          <div className="inline-actions">
                            <input
                              aria-label={`Usuario de ${user.full_name}`}
                              onChange={(event) =>
                                setEditedUsernames((currentValues) => ({
                                  ...currentValues,
                                  [user.id]: event.target.value,
                                }))
                              }
                              type="text"
                              value={editedUsernames[user.id] ?? user.username}
                            />
                            <button
                              disabled={isUpdating}
                              onClick={() =>
                                void updateUser(user.id, {
                                  username:
                                    editedUsernames[user.id] ?? user.username,
                                })
                              }
                              type="button"
                            >
                              Guardar
                            </button>
                          </div>
                        )}
                      </td>
                      <td>
                        {isCurrentUser ? (
                          roleLabels[user.role]
                        ) : (
                          <select
                            disabled={isUpdating}
                            onChange={(event) =>
                              void updateUser(user.id, {
                                role: event.target.value as UserRole,
                              })
                            }
                            value={user.role}
                          >
                            <option value="admin">Administrador</option>
                            <option value="operator">Operador</option>
                            <option value="management">Gerencia</option>
                          </select>
                        )}
                      </td>
                      <td>{user.active ? "Activo" : "Inactivo"}</td>
                      <td>
                        {isCurrentUser ? (
                          "Sesión actual"
                        ) : (
                          <button
                            disabled={isUpdating}
                            onClick={() =>
                              void updateUser(user.id, {
                                active: !user.active,
                              })
                            }
                            type="button"
                          >
                            {user.active ? "Desactivar" : "Activar"}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

export default UsersPage;
