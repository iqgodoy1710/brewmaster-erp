import { useState } from "react";
import {
  BrowserRouter,
  Navigate,
  NavLink,
  Route,
  Routes,
} from "react-router-dom";

import "./App.css";
import DashboardPage from "./pages/DashboardPage";
import RawMaterialsPage from "./pages/RawMaterialsPage";
import FinishedProductsPage from "./pages/FinishedProductsPage";
import SalesPage from "./pages/SalesPage";
import ProductionPage from "./pages/ProductionPage";
import PackagingPage from "./pages/PackagingPage";
import RawMaterialMovementsPage from "./pages/RawMaterialMovementsPage";
import CustomersPage from "./pages/CustomersPage";
import BeersPage from "./pages/BeersPage";
import PackagingFormatsPage from "./pages/PackagingFormatsPage";
import BeerPresentationsPage from "./pages/BeerPresentationsPage";
import RecipesPage from "./pages/RecipesPage";
import RecipeIngredientsPage from "./pages/RecipeIngredientsPage";
import BeerPresentationPackagingMaterialsPage from "./pages/BeerPresentationPackagingMaterialsPage";
import SuppliersPage from "./pages/SuppliersPage";
import CategoriesPage from "./pages/CategoriesPage";
import UnitsPage from "./pages/UnitsPage";
import SaleDetailsPage from "./pages/SaleDetailsPage";
import { isDemoMode } from "./lib/api";

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <div className="topbar-brand">
            <div>
              <p className="brand">BrewMaster ERP</p>
              <p className="subtitle">Panel operativo</p>
            </div>

            <button
              aria-controls="primary-navigation"
              aria-expanded={isMenuOpen}
              className="menu-button"
              onClick={() => setIsMenuOpen((isOpen) => !isOpen)}
              type="button"
            >
              {isMenuOpen ? "Cerrar menú" : "Menú"}
            </button>
          </div>

          <nav
            id="primary-navigation"
            aria-label="Navegación principal"
            className={`navigation ${isMenuOpen ? "navigation-open" : ""}`}
            onClick={() => setIsMenuOpen(false)}
          >
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/"
              end
            >
              Dashboard
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/insumos"
            >
              Insumos
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/producto-terminado"
            >
              Producto terminado
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/ventas"
            >
              Ventas
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/produccion"
            >
              Producción
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/envasado"
            >
              Envasado
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/movimientos-insumos"
            >
              Mov. insumos
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/clientes"
            >
              Clientes
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/cervezas"
            >
              Cervezas
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/formatos-envasado"
            >
              Formatos
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/presentaciones"
            >
              Presentaciones
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/recetas"
            >
              Recetas
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/ingredientes-receta"
            >
              Ingredientes
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/materiales-envasado"
            >
              Materiales
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/proveedores"
            >
              Proveedores
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/categorias"
            >
              Categorías
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/unidades"
            >
              Unidades
            </NavLink>
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/detalle-ventas"
            >
              Detalle ventas
            </NavLink>
          </nav>
        </header>
        {isDemoMode && (
          <p className="demo-banner" role="status">
            Demo pública: explorá los flujos y datos de ejemplo. Los cambios
            están deshabilitados.
          </p>
        )}

        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/insumos" element={<RawMaterialsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route
            path="/producto-terminado"
            element={<FinishedProductsPage />}
          />
          <Route path="/ventas" element={<SalesPage />} />
          <Route path="/produccion" element={<ProductionPage />} />
          <Route path="/envasado" element={<PackagingPage />} />
          <Route
            path="/movimientos-insumos"
            element={<RawMaterialMovementsPage />}
          />
          <Route path="/clientes" element={<CustomersPage />} />
          <Route path="/cervezas" element={<BeersPage />} />
          <Route path="/formatos-envasado" element={<PackagingFormatsPage />} />
          <Route path="/presentaciones" element={<BeerPresentationsPage />} />
          <Route path="/recetas" element={<RecipesPage />} />
          <Route
            path="/ingredientes-receta"
            element={<RecipeIngredientsPage />}
          />
          <Route
            path="/materiales-envasado"
            element={<BeerPresentationPackagingMaterialsPage />}
          />
          <Route path="/proveedores" element={<SuppliersPage />} />
          <Route path="/categorias" element={<CategoriesPage />} />
          <Route path="/unidades" element={<UnitsPage />} />
          <Route path="/detalle-ventas" element={<SaleDetailsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
