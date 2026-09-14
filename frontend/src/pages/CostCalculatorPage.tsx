import { useEffect, useMemo, useState } from "react";

import "../App.css";
import { apiGet } from "../lib/api";
import type {
  BeerPresentation,
  BeerPresentationCostEstimate,
  Recipe,
  Beer,
  PackagingFormat,
} from "../types/api";
import { Link } from "react-router-dom";

const formatCurrency = (value: string | number) =>
  new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
    currencyDisplay: "narrowSymbol",
  }).format(Number(value));

const formatQuantity = (value: string) =>
  new Intl.NumberFormat("es-ES", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));

function CostCalculatorPage() {
  const [presentations, setPresentations] = useState<BeerPresentation[]>([]);
  const [beers, setBeers] = useState<Beer[]>([]);
  const [formats, setFormats] = useState<PackagingFormat[]>([]);
  const [formatFilter, setFormatFilter] = useState<"all" | "keg" | "bottle">(
    "all",
  );
  const [styleFilter, setStyleFilter] = useState("");
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [presentationId, setPresentationId] = useState("");
  const [recipeId, setRecipeId] = useState("");
  const [desiredMargin, setDesiredMargin] = useState("40");
  const [estimate, setEstimate] = useState<BeerPresentationCostEstimate | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(true);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [presentationsData, recipesData, beersData, formatsData] =
          await Promise.all([
            apiGet<BeerPresentation[]>("/beer-presentations/"),
            apiGet<Recipe[]>("/recipes/"),
            apiGet<Beer[]>("/beers/"),
            apiGet<PackagingFormat[]>("/packaging-formats/"),
          ]);

        setPresentations(presentationsData);
        setRecipes(recipesData);
        setBeers(beersData);
        setFormats(formatsData);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "No se pudieron cargar los datos de costos.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    void loadData();
  }, []);

  const availableStyles = useMemo(
    () =>
      [
        ...new Set(
          beers
            .map((beer) => beer.style?.trim())
            .filter((style): style is string => Boolean(style)),
        ),
      ].sort((a, b) => a.localeCompare(b, "es")),
    [beers],
  );

  const filteredPresentations = useMemo(() => {
    const beerById = new Map(beers.map((beer) => [beer.id, beer]));
    const formatById = new Map(formats.map((format) => [format.id, format]));

    return presentations.filter((presentation) => {
      const format = formatById.get(presentation.packaging_format_id);
      const beer = beerById.get(presentation.beer_id);

      return (
        (formatFilter === "all" || format?.format_type === formatFilter) &&
        (!styleFilter || beer?.style === styleFilter)
      );
    });
  }, [beers, formats, formatFilter, presentations, styleFilter]);

  const selectedPresentation = presentations.find(
    (presentation) => presentation.id === Number(presentationId),
  );

  const compatibleRecipes = useMemo(() => {
    if (!selectedPresentation) {
      return [];
    }

    return recipes.filter(
      (recipe) => recipe.beer_id === selectedPresentation.beer_id,
    );
  }, [presentations, recipes, selectedPresentation]);

  const marginAsPercentage = Number(desiredMargin);

  const suggestedPrice = useMemo(() => {
    if (
      !estimate ||
      !Number.isFinite(marginAsPercentage) ||
      marginAsPercentage < 0 ||
      marginAsPercentage >= 100
    ) {
      return null;
    }

    return Number(estimate.total_unit_cost) / (1 - marginAsPercentage / 100);
  }, [estimate, marginAsPercentage]);

  const costPerLiter = useMemo(() => {
    if (!estimate) {
      return null;
    }

    const volume = Number(estimate.packaging_volume_liters);
    const totalCost = Number(estimate.total_unit_cost);

    if (
      !Number.isFinite(volume) ||
      volume <= 0 ||
      !Number.isFinite(totalCost)
    ) {
      return null;
    }

    return totalCost / volume;
  }, [estimate]);

  function handlePresentationChange(value: string) {
    setPresentationId(value);
    setRecipeId("");
    setEstimate(null);
    setError(null);
  }

  async function calculateEstimate() {
    if (!presentationId || !recipeId) {
      setError("Seleccioná una presentación y una receta.");
      return;
    }

    setError(null);
    setIsCalculating(true);

    try {
      const data = await apiGet<BeerPresentationCostEstimate>(
        `/beer-presentations/${presentationId}/cost-estimate` +
          `?recipe_id=${recipeId}`,
      );

      setEstimate(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "No se pudo calcular el costo.",
      );
    } finally {
      setIsCalculating(false);
    }
  }

  return (
    <main className="dashboard">
      <section className="page-heading">
        <p className="eyebrow">Comercial</p>
        <h1>Calculadora de costos</h1>
        <p>
          Estimá el costo unitario de cada presentación a partir de receta,
          insumos y materiales de envasado.
        </p>
      </section>

      {error && (
        <p className="error-message" role="alert">
          {error}
        </p>
      )}

      {isLoading ? (
        <p>Cargando datos para el cálculo...</p>
      ) : (
        <>
          <section className="panel sales-form-panel">
            <h2>Datos del cálculo</h2>
            <div className="table-toolbar">
              <label>
                Tipo de presentación
                <select
                  onChange={(event) => {
                    setFormatFilter(
                      event.target.value as "all" | "keg" | "bottle",
                    );
                    handlePresentationChange("");
                  }}
                  value={formatFilter}
                >
                  <option value="all">Todos</option>
                  <option value="keg">Barriles</option>
                  <option value="bottle">Botellas</option>
                </select>
              </label>

              <label>
                Estilo
                <select
                  onChange={(event) => {
                    setStyleFilter(event.target.value);
                    handlePresentationChange("");
                  }}
                  value={styleFilter}
                >
                  <option value="">Todos los estilos</option>
                  {availableStyles.map((style) => (
                    <option key={style} value={style}>
                      {style}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-grid">
              <label>
                Presentación
                <select
                  onChange={(event) =>
                    handlePresentationChange(event.target.value)
                  }
                  value={presentationId}
                >
                  <option value="">Seleccioná una presentación</option>
                  {filteredPresentations.map((presentation) => (
                    <option key={presentation.id} value={presentation.id}>
                      {presentation.code} · {presentation.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Receta
                <select
                  disabled={!selectedPresentation}
                  onChange={(event) => {
                    setRecipeId(event.target.value);
                    setEstimate(null);
                    setError(null);
                  }}
                  value={recipeId}
                >
                  <option value="">
                    {selectedPresentation
                      ? "Seleccioná una receta"
                      : "Seleccioná primero una presentación"}
                  </option>
                  {compatibleRecipes.map((recipe) => (
                    <option key={recipe.id} value={recipe.id}>
                      Versión {recipe.version} ·{" "}
                      {formatQuantity(recipe.target_volume_liters)} L
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Margen deseado (%)
                <input
                  max="99.99"
                  min="0"
                  onChange={(event) => setDesiredMargin(event.target.value)}
                  step="0.01"
                  type="number"
                  value={desiredMargin}
                />
              </label>
            </div>
            {filteredPresentations.length === 0 && (
              <p className="empty-state">
                No hay presentaciones para los filtros seleccionados.
              </p>
            )}

            {selectedPresentation && compatibleRecipes.length === 0 && (
              <p className="empty-state">
                Esta cerveza no tiene recetas disponibles.
              </p>
            )}

            <button
              disabled={!presentationId || !recipeId || isCalculating}
              onClick={calculateEstimate}
              type="button"
            >
              {isCalculating ? "Calculando..." : "Calcular costo"}
            </button>
          </section>

          {estimate && (
            <>
              <section className="summary-grid sales-summary">
                <article className="summary-card">
                  <p>Costo de cerveza</p>
                  <strong>{formatCurrency(estimate.beer_cost)}</strong>
                </article>

                <article className="summary-card">
                  <p>Costo de envasado</p>
                  <strong>
                    {formatCurrency(estimate.packaging_material_cost)}
                  </strong>
                </article>

                <article className="summary-card">
                  <p>Costo unitario estimado</p>
                  <strong>{formatCurrency(estimate.total_unit_cost)}</strong>
                </article>

                <article className="summary-card">
                  <p>Costo estimado por litro</p>
                  <strong>
                    {costPerLiter === null
                      ? "—"
                      : `${formatCurrency(costPerLiter)} / L`}
                  </strong>
                </article>
              </section>

              <section className="panel">
                <h2>Precio sugerido</h2>

                {suggestedPrice === null ? (
                  <p className="error-message">
                    El margen debe ser mayor o igual a 0% y menor a 100%.
                  </p>
                ) : (
                  <div className="form-actions">
                    <p className="draft-total">
                      Con un margen de{" "}
                      <strong>{formatQuantity(desiredMargin)}%</strong>, el
                      precio sugerido es{" "}
                      <strong>{formatCurrency(suggestedPrice)}</strong>.
                    </p>

                    <Link
                      className="secondary-button"
                      to={
                        `/precios?presentation_id=${estimate.beer_presentation_id}` +
                        `&unit_price=${suggestedPrice.toFixed(2)}`
                      }
                    >
                      Usar este precio en la lista
                    </Link>
                  </div>
                )}
              </section>

              <section className="panel">
                <h2>Detalle del costo estimado</h2>
                <p className="form-help">
                  Receta versión {estimate.recipe_version} · volumen objetivo{" "}
                  {formatQuantity(estimate.recipe_target_volume_liters)} L ·
                  presentación de{" "}
                  {formatQuantity(estimate.packaging_volume_liters)} L.
                </p>

                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Origen</th>
                        <th>Insumo</th>
                        <th>Cantidad</th>
                        <th>Costo unitario</th>
                        <th>Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
                      {estimate.components.map((component) => (
                        <tr
                          key={
                            `${component.component_type}-` +
                            component.raw_material_id
                          }
                        >
                          <td>
                            {component.component_type === "beer"
                              ? "Cerveza"
                              : "Envasado"}
                          </td>
                          <td>
                            {component.raw_material_name}
                            <br />
                            <small>{component.raw_material_code}</small>
                          </td>
                          <td>
                            {formatQuantity(component.quantity)}{" "}
                            {component.unit_symbol}
                          </td>
                          <td>{formatCurrency(component.unit_cost)}</td>
                          <td>{formatCurrency(component.subtotal)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}
        </>
      )}
    </main>
  );
}

export default CostCalculatorPage;
