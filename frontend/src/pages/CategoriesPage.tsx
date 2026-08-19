import { useCallback, useEffect, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type { Category } from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

function CategoriesPage() {
  const currentUser = useCurrentUser();

  const canManageCatalog = hasRole(currentUser, "admin");
  const [categories, setCategories] = useState<Category[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadCategories = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await apiGet<Category[]>("/categories/");
      setCategories(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar las categorías.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadCategories();
  }, [loadCategories]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!name.trim()) {
      setError("Ingresá el nombre de la categoría.");
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      await apiPost<Category>("/categories/", {
        name: name.trim(),
        description: description.trim() || null,
      });

      setName("");
      setDescription("");
      setSuccess("Categoría creada correctamente.");

      await loadCategories();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear la categoría.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Categorías de insumos</h1>
        <p>Organizá las materias primas según su tipo.</p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && <p className="success-message">{success}</p>}
      {canManageCatalog ? (
        <section className="panel">
          <h2>Nueva categoría</h2>

          <form className="sale-form" onSubmit={handleSubmit}>
            <div className="form-grid">
              <label>
                Nombre
                <input
                  placeholder="Ej.: Lúpulos"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
              </label>

              <label>
                Descripción
                <input
                  placeholder="Descripción opcional"
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                />
              </label>
            </div>

            <button disabled={isSaving} type="submit">
              {isSaving ? "Creando..." : "Crear categoría"}
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
        <h2>Categorías registradas</h2>

        {isLoading ? (
          <p>Cargando categorías...</p>
        ) : categories.length === 0 ? (
          <p className="empty-state">Todavía no hay categorías registradas.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Categoría</th>
                  <th>Descripción</th>
                </tr>
              </thead>
              <tbody>
                {categories.map((category) => (
                  <tr key={category.id}>
                    <td>{category.name}</td>
                    <td>{category.description ?? "—"}</td>
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

export default CategoriesPage;
