import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { hasRole, useCurrentUser } from "../lib/auth";
import { apiGet, apiPatch, apiPost } from "../lib/api";
import type { Beer, Recipe } from "../types/api";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

function RecipesPage() {
  const currentUser = useCurrentUser();

  const canManageRecipes = hasRole(currentUser, "admin");

  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [beers, setBeers] = useState<Beer[]>([]);

  const [beerId, setBeerId] = useState("");
  const [version, setVersion] = useState("");
  const [targetVolume, setTargetVolume] = useState("");
  const [notes, setNotes] = useState("");

  const [editingRecipe, setEditingRecipe] = useState<Recipe | null>(null);
  const [editingTargetVolume, setEditingTargetVolume] = useState("");
  const [editingNotes, setEditingNotes] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [recipesData, beersData] = await Promise.all([
        apiGet<Recipe[]>("/recipes/"),
        apiGet<Beer[]>("/beers/"),
      ]);

      setRecipes(recipesData);
      setBeers(beersData);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar las recetas.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  async function createRecipe(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const parsedVersion = Number(version);
    const parsedTargetVolume = Number(targetVolume);

    if (!beerId) {
      setError("Seleccioná una cerveza.");
      return;
    }

    if (!Number.isInteger(parsedVersion) || parsedVersion <= 0) {
      setError("La versión debe ser un entero mayor a cero.");
      return;
    }

    if (!Number.isFinite(parsedTargetVolume) || parsedTargetVolume <= 0) {
      setError("El volumen objetivo debe ser mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const recipe = await apiPost<Recipe>("/recipes/", {
        beer_id: Number(beerId),
        version: parsedVersion,
        target_volume_liters: targetVolume,
        notes: notes.trim() || null,
      });

      setBeerId("");
      setVersion("");
      setTargetVolume("");
      setNotes("");

      setSuccess(`La receta #${recipe.id} fue creada correctamente.`);

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo crear la receta.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  function startEditing(recipe: Recipe) {
    setEditingRecipe(recipe);
    setEditingTargetVolume(recipe.target_volume_liters);
    setEditingNotes(recipe.notes ?? "");
    setError(null);
    setSuccess(null);
  }

  function cancelEditing() {
    setEditingRecipe(null);
    setEditingTargetVolume("");
    setEditingNotes("");
  }

  async function updateRecipe(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!editingRecipe) {
      return;
    }

    const parsedTargetVolume = Number(editingTargetVolume);

    if (!Number.isFinite(parsedTargetVolume) || parsedTargetVolume <= 0) {
      setError("El volumen objetivo debe ser mayor a cero.");
      return;
    }

    setError(null);
    setSuccess(null);
    setIsUpdating(true);

    try {
      const recipe = await apiPatch<Recipe>(
        `/recipes/${editingRecipe.id}`,
        {
          target_volume_liters: editingTargetVolume,
          notes: editingNotes.trim() || null,
        },
      );

      cancelEditing();
      setSuccess(`La receta #${recipe.id} fue actualizada correctamente.`);

      await loadData();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo actualizar la receta.",
      );
    } finally {
      setIsUpdating(false);
    }
  }

  const beerName = (id: number) =>
    beers.find((beer) => beer.id === id)?.name ?? "—";

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Configuración</p>
        <h1>Recetas</h1>
        <p>Definí versiones y volumen objetivo para cada cerveza.</p>
      </section>

      {isLoading && <p>Cargando recetas...</p>}

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {success && (
        <p className="success-message" role="status">
          {success}
        </p>
      )}

      {!isLoading && hasLoaded && (
        <>
          {canManageRecipes ? (
            <>
              <section className="panel sales-form-panel">
                <h2>Nueva receta</h2>

                <form className="sale-form" onSubmit={createRecipe}>
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
                      Versión
                      <input
                        min="1"
                        onChange={(event) => setVersion(event.target.value)}
                        required
                        step="1"
                        type="number"
                        value={version}
                      />
                    </label>
                  </div>

                  <div className="form-grid">
                    <label>
                      Volumen objetivo (L)
                      <input
                        min="0.001"
                        onChange={(event) =>
                          setTargetVolume(event.target.value)
                        }
                        required
                        step="0.001"
                        type="number"
                        value={targetVolume}
                      />
                    </label>

                    <label>
                      Notas
                      <input
                        onChange={(event) => setNotes(event.target.value)}
                        placeholder="Notas opcionales."
                        value={notes}
                      />
                    </label>
                  </div>

                  <button disabled={isSaving} type="submit">
                    {isSaving ? "Creando receta..." : "Crear receta"}
                  </button>
                </form>
              </section>

              {editingRecipe && (
                <section className="panel sales-form-panel">
                  <h2>
                    Editar receta #{editingRecipe.id} · Versión{" "}
                    {editingRecipe.version}
                  </h2>

                  <p className="form-help">
                    La cerveza y versión no se modifican. Si la receta ya tiene
                    lotes asociados, deberás crear una versión nueva.
                  </p>

                  <form className="sale-form" onSubmit={updateRecipe}>
                    <div className="form-grid">
                      <label>
                        Volumen objetivo (L)
                        <input
                          min="0.001"
                          onChange={(event) =>
                            setEditingTargetVolume(event.target.value)
                          }
                          required
                          step="0.001"
                          type="number"
                          value={editingTargetVolume}
                        />
                      </label>

                      <label>
                        Notas
                        <input
                          onChange={(event) =>
                            setEditingNotes(event.target.value)
                          }
                          placeholder="Notas opcionales."
                          value={editingNotes}
                        />
                      </label>
                    </div>

                    <div className="button-row">
                      <button disabled={isUpdating} type="submit">
                        {isUpdating
                          ? "Guardando cambios..."
                          : "Guardar cambios"}
                      </button>

                      <button
                        disabled={isUpdating}
                        onClick={cancelEditing}
                        type="button"
                      >
                        Cancelar
                      </button>
                    </div>
                  </form>
                </section>
              )}
            </>
          ) : (
            <section className="panel">
              <p className="empty-state">
                Solo los administradores pueden crear o modificar recetas.
              </p>
            </section>
          )}

          <section className="panel">
            <h2>Recetas registradas</h2>

            {recipes.length === 0 ? (
              <p className="empty-state">
                Todavía no hay recetas registradas.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Cerveza</th>
                      <th>Versión</th>
                      <th>Volumen objetivo</th>
                      <th>Notas</th>
                      {canManageRecipes && <th>Acciones</th>}
                    </tr>
                  </thead>

                  <tbody>
                    {recipes.map((recipe) => (
                      <tr key={recipe.id}>
                        <td>{recipe.id}</td>
                        <td>{beerName(recipe.beer_id)}</td>
                        <td>{recipe.version}</td>
                        <td>
                          {formatNumber(recipe.target_volume_liters)} L
                        </td>
                        <td>{recipe.notes ?? "—"}</td>

                        {canManageRecipes && (
                          <td>
                            <button
                              onClick={() => startEditing(recipe)}
                              type="button"
                            >
                              Editar
                            </button>
                          </td>
                        )}
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

export default RecipesPage;