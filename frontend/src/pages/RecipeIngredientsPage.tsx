import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import "../App.css";
import { apiDelete, apiGet, apiPatch, apiPost } from "../lib/api";
import type {
  Beer,
  Category,
  RawMaterialReference,
  Recipe,
  RecipeIngredient,
} from "../types/api";
import { hasRole, useCurrentUser } from "../lib/auth";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

function RecipeIngredientsPage() {
  const currentUser = useCurrentUser();

  const canManageCatalog =
    hasRole(currentUser, "admin") || hasRole(currentUser, "operator");

  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [beers, setBeers] = useState<Beer[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [rawMaterials, setRawMaterials] = useState<
    RawMaterialReference[]
  >([]);
  const [ingredients, setIngredients] = useState<RecipeIngredient[]>([]);

  const [recipeId, setRecipeId] = useState("");
  const [rawMaterialId, setRawMaterialId] = useState("");
  const [requiredQuantity, setRequiredQuantity] = useState("");

  const [rawMaterialSearch, setRawMaterialSearch] = useState("");
  const [categoryFilterId, setCategoryFilterId] = useState("");

  const [editingIngredient, setEditingIngredient] =
    useState<RecipeIngredient | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadBaseData = useCallback(async () => {
    try {
      const [recipesData, rawMaterialsData, beersData, categoriesData] =
        await Promise.all([
          apiGet<Recipe[]>("/recipes/"),
          apiGet<RawMaterialReference[]>("/raw-materials/references"),
          apiGet<Beer[]>("/beers/"),
          apiGet<Category[]>("/categories/"),
        ]);

      setRecipes(recipesData);
      setRawMaterials(rawMaterialsData);
      setBeers(beersData);
      setCategories(categoriesData);
      setHasLoaded(true);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar recetas e insumos.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadIngredients = useCallback(async (currentRecipeId: string) => {
    if (!currentRecipeId) {
      setIngredients([]);
      return;
    }

    try {
      const data = await apiGet<RecipeIngredient[]>(
        `/recipes/${currentRecipeId}/ingredients`,
      );

      setIngredients(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudieron cargar los ingredientes.",
      );
    }
  }, []);

  useEffect(() => {
    void loadBaseData();
  }, [loadBaseData]);

  useEffect(() => {
    void loadIngredients(recipeId);
  }, [loadIngredients, recipeId]);

  const selectedRecipe = useMemo(
    () => recipes.find((recipe) => recipe.id === Number(recipeId)),
    [recipeId, recipes],
  );

  const selectedRawMaterial = useMemo(
    () =>
      rawMaterials.find(
        (rawMaterial) => rawMaterial.id === Number(rawMaterialId),
      ),
    [rawMaterialId, rawMaterials],
  );

  const filteredRawMaterials = useMemo(() => {
    const normalizedSearch = rawMaterialSearch.trim().toLowerCase();

    return rawMaterials.filter((rawMaterial) => {
      const matchesCategory =
        !categoryFilterId ||
        rawMaterial.category_id === Number(categoryFilterId);

      const matchesSearch =
        !normalizedSearch ||
        rawMaterial.code.toLowerCase().includes(normalizedSearch) ||
        rawMaterial.name.toLowerCase().includes(normalizedSearch);

      return matchesCategory && matchesSearch;
    });
  }, [categoryFilterId, rawMaterialSearch, rawMaterials]);

  const rawMaterialById = (id: number) =>
    rawMaterials.find((rawMaterial) => rawMaterial.id === id);

  const recipeLabel = (recipe: Recipe) => {
    const beerName =
      beers.find((beer) => beer.id === recipe.beer_id)?.name ??
      `Cerveza #${recipe.beer_id}`;

    return (
      `${beerName} · Versión ${recipe.version} · ` +
      `${formatNumber(recipe.target_volume_liters)} L`
    );
  };

  function resetIngredientForm() {
    setEditingIngredient(null);
    setRawMaterialId("");
    setRequiredQuantity("");
  }

  function handleRecipeChange(value: string) {
    setRecipeId(value);
    resetIngredientForm();
    setError(null);
    setSuccess(null);
  }

  function startEditing(ingredient: RecipeIngredient) {
    setEditingIngredient(ingredient);
    setRawMaterialId(String(ingredient.raw_material_id));
    setRequiredQuantity(ingredient.required_quantity);
    setError(null);
    setSuccess(null);
  }

  async function saveIngredient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const quantity = Number(requiredQuantity);

    if (!recipeId || !rawMaterialId) {
      setError("Seleccioná una receta y un insumo.");
      return;
    }

    if (!Number.isFinite(quantity) || quantity <= 0) {
      setError("La cantidad requerida debe ser mayor a cero.");
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      if (editingIngredient) {
        await apiPatch<RecipeIngredient>(
          `/recipe-ingredients/${editingIngredient.id}`,
          {
            raw_material_id: Number(rawMaterialId),
            required_quantity: requiredQuantity,
          },
        );

        setSuccess("El ingrediente fue actualizado correctamente.");
      } else {
        await apiPost<RecipeIngredient>("/recipe-ingredients/", {
          recipe_id: Number(recipeId),
          raw_material_id: Number(rawMaterialId),
          required_quantity: requiredQuantity,
        });

        setSuccess("El ingrediente fue agregado correctamente.");
      }

      resetIngredientForm();
      await loadIngredients(recipeId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo guardar el ingrediente.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function deactivateIngredient(ingredient: RecipeIngredient) {
    const rawMaterial = rawMaterialById(ingredient.raw_material_id);

    const confirmed = window.confirm(
      `¿Eliminar "${rawMaterial?.name ?? "este insumo"}" de la receta?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccess(null);

      await apiDelete<RecipeIngredient>(
        `/recipe-ingredients/${ingredient.id}`,
      );

      if (editingIngredient?.id === ingredient.id) {
        resetIngredientForm();
      }

      setSuccess("El ingrediente fue eliminado de la receta.");
      await loadIngredients(recipeId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo eliminar el ingrediente.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Ingredientes de recetas</h1>
        <p>Definí los insumos requeridos para cada receta.</p>
      </section>

      {isLoading && <p>Cargando ingredientes...</p>}

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
              <h2>
                {editingIngredient
                  ? "Editar ingrediente"
                  : "Agregar ingrediente"}
              </h2>

              <form className="sale-form" onSubmit={saveIngredient}>
                <div className="form-grid">
                  <label>
                    Receta
                    <select
                      disabled={editingIngredient !== null}
                      onChange={(event) =>
                        handleRecipeChange(event.target.value)
                      }
                      required
                      value={recipeId}
                    >
                      <option value="">Seleccioná una receta</option>
                      {recipes.map((recipe) => (
                        <option key={recipe.id} value={recipe.id}>
                          {recipeLabel(recipe)}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Buscar insumo
                    <input
                      onChange={(event) =>
                        setRawMaterialSearch(event.target.value)
                      }
                      placeholder="Código o nombre"
                      type="search"
                      value={rawMaterialSearch}
                    />
                  </label>

                  <label>
                    Categoría
                    <select
                      onChange={(event) =>
                        setCategoryFilterId(event.target.value)
                      }
                      value={categoryFilterId}
                    >
                      <option value="">Todas las categorías</option>
                      {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </label>

                  <label>
                    Insumo
                    <select
                      onChange={(event) =>
                        setRawMaterialId(event.target.value)
                      }
                      required
                      value={rawMaterialId}
                    >
                      <option value="">Seleccioná un insumo</option>
                      {filteredRawMaterials.map((rawMaterial) => (
                        <option key={rawMaterial.id} value={rawMaterial.id}>
                          {rawMaterial.code} · {rawMaterial.name} ·{" "}
                          {rawMaterial.unit_symbol}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                {filteredRawMaterials.length === 0 && (
                  <p className="form-help">
                    No hay insumos que coincidan con la búsqueda o categoría.
                  </p>
                )}

                <label>
                  {selectedRawMaterial
                    ? `Cantidad requerida (${selectedRawMaterial.unit_symbol})`
                    : "Cantidad requerida"}
                  <input
                    min="0.001"
                    onChange={(event) =>
                      setRequiredQuantity(event.target.value)
                    }
                    required
                    step="0.001"
                    type="number"
                    value={requiredQuantity}
                  />
                </label>

                <div className="inline-actions">
                  <button disabled={isSaving} type="submit">
                    {isSaving
                      ? "Guardando..."
                      : editingIngredient
                        ? "Guardar cambios"
                        : "Agregar ingrediente"}
                  </button>

                  {editingIngredient && (
                    <button
                      disabled={isSaving}
                      onClick={resetIngredientForm}
                      type="button"
                    >
                      Cancelar edición
                    </button>
                  )}
                </div>
              </form>
            </section>
          ) : (
            <section className="panel">
              <h2>Consultar ingredientes</h2>

              <label>
                Receta
                <select
                  onChange={(event) =>
                    handleRecipeChange(event.target.value)
                  }
                  value={recipeId}
                >
                  <option value="">Seleccioná una receta</option>
                  {recipes.map((recipe) => (
                    <option key={recipe.id} value={recipe.id}>
                      {recipeLabel(recipe)}
                    </option>
                  ))}
                </select>
              </label>
            </section>
          )}

          <section className="panel">
            <h2>
              {selectedRecipe
                ? `Ingredientes de ${recipeLabel(selectedRecipe)}`
                : "Ingredientes de la receta"}
            </h2>

            {!selectedRecipe ? (
              <p className="empty-state">
                Seleccioná una receta para ver sus ingredientes.
              </p>
            ) : ingredients.length === 0 ? (
              <p className="empty-state">
                Esta receta todavía no tiene ingredientes.
              </p>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Código</th>
                      <th>Insumo</th>
                      <th>Unidad</th>
                      <th>Cantidad requerida</th>
                      {canManageCatalog && <th>Acciones</th>}
                    </tr>
                  </thead>

                  <tbody>
                    {ingredients.map((ingredient) => {
                      const rawMaterial = rawMaterialById(
                        ingredient.raw_material_id,
                      );

                      return (
                        <tr key={ingredient.id}>
                          <td>{rawMaterial?.code ?? "—"}</td>
                          <td>{rawMaterial?.name ?? "—"}</td>
                          <td>{rawMaterial?.unit_symbol ?? "—"}</td>
                          <td>
                            {formatNumber(ingredient.required_quantity)}
                          </td>

                          {canManageCatalog && (
                            <td>
                              <div className="inline-actions">
                                <button
                                  disabled={isSaving}
                                  onClick={() => startEditing(ingredient)}
                                  type="button"
                                >
                                  Editar
                                </button>

                                <button
                                  disabled={isSaving}
                                  onClick={() =>
                                    void deactivateIngredient(ingredient)
                                  }
                                  type="button"
                                >
                                  Eliminar
                                </button>
                              </div>
                            </td>
                          )}
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
    </main>
  );
}

export default RecipeIngredientsPage;