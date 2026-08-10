import { useCallback, useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet, apiPost } from "../lib/api";
import type {
  RawMaterial,
  Recipe,
  RecipeIngredient,
} from "../types/api";

const formatNumber = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  }).format(Number(value));

function RecipeIngredientsPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [rawMaterials, setRawMaterials] = useState<RawMaterial[]>([]);
  const [ingredients, setIngredients] = useState<RecipeIngredient[]>([]);
  const [recipeId, setRecipeId] = useState("");
  const [rawMaterialId, setRawMaterialId] = useState("");
  const [requiredQuantity, setRequiredQuantity] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadBaseData = useCallback(async () => {
    try {
      const [recipesData, rawMaterialsData] = await Promise.all([
        apiGet<Recipe[]>("/recipes/"),
        apiGet<RawMaterial[]>("/raw-materials/"),
      ]);

      setRecipes(recipesData);
      setRawMaterials(rawMaterialsData);
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
    loadBaseData();
  }, [loadBaseData]);

  useEffect(() => {
    loadIngredients(recipeId);
  }, [loadIngredients, recipeId]);

  const selectedRecipe = useMemo(
    () => recipes.find((recipe) => recipe.id === Number(recipeId)),
    [recipeId, recipes],
  );

  async function createIngredient(
    event: React.FormEvent<HTMLFormElement>,
  ) {
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

    setError(null);
    setSuccess(null);
    setIsSaving(true);

    try {
      const ingredient = await apiPost<RecipeIngredient>(
        "/recipe-ingredients/",
        {
          recipe_id: Number(recipeId),
          raw_material_id: Number(rawMaterialId),
          required_quantity: requiredQuantity,
        },
      );

      setRawMaterialId("");
      setRequiredQuantity("");
      setSuccess("El ingrediente fue agregado correctamente.");

      await loadIngredients(String(ingredient.recipe_id));
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo agregar el ingrediente.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  const rawMaterialName = (id: number) =>
    rawMaterials.find((rawMaterial) => rawMaterial.id === id)?.name ?? "—";

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Catálogo</p>
        <h1>Ingredientes de recetas</h1>
        <p>Definí los insumos requeridos para cada receta.</p>
      </section>

      {isLoading && <p>Cargando ingredientes...</p>}
      {error && <p className="error-message" role="alert">{error}</p>}
      {success && <p className="success-message">{success}</p>}

      {!isLoading && hasLoaded && (
        <>
          <section className="panel sales-form-panel">
            <h2>Agregar ingrediente</h2>

            <form className="sale-form" onSubmit={createIngredient}>
              <div className="form-grid">
                <label>
                  Receta
                  <select
                    onChange={(event) => setRecipeId(event.target.value)}
                    required
                    value={recipeId}
                  >
                    <option value="">Seleccioná una receta</option>
                    {recipes.map((recipe) => (
                      <option key={recipe.id} value={recipe.id}>
                        Receta #{recipe.id} · Versión {recipe.version}
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
                    {rawMaterials.map((rawMaterial) => (
                      <option key={rawMaterial.id} value={rawMaterial.id}>
                        {rawMaterial.code} · {rawMaterial.name}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label>
                Cantidad requerida
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

              <button disabled={isSaving} type="submit">
                {isSaving ? "Agregando ingrediente..." : "Agregar ingrediente"}
              </button>
            </form>
          </section>

          <section className="panel">
            <h2>
              {selectedRecipe
                ? `Ingredientes de la receta #${selectedRecipe.id}`
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
                      <th>Insumo</th>
                      <th>Cantidad requerida</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ingredients.map((ingredient) => (
                      <tr key={ingredient.id}>
                        <td>
                          {rawMaterialName(ingredient.raw_material_id)}
                        </td>
                        <td>
                          {formatNumber(ingredient.required_quantity)}
                        </td>
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

export default RecipeIngredientsPage;