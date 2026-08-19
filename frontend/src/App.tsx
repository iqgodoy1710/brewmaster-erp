import { useEffect, useState } from "react";
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
import LoginPage from "./pages/LoginPage";
import {
  apiGet,
  apiPost,
  clearAccessToken,
  getAccessToken,
  isAuthRequired,
  isDemoMode,
  setAccessToken,
} from "./lib/api";
import type { AuthenticatedUser, TokenResponse } from "./types/api";
import { AuthProvider } from "./lib/auth";
import UsersPage from "./pages/UsersPage";

function AppContent() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(isAuthRequired);

  useEffect(() => {
    async function loadSession() {
      if (!isAuthRequired || !getAccessToken()) {
        setIsAuthLoading(false);
        return;
      }

      try {
        const currentUser = await apiGet<AuthenticatedUser>("/auth/me");
        setUser(currentUser);
      } catch {
        clearAccessToken();
        setUser(null);
      } finally {
        setIsAuthLoading(false);
      }
    }

    void loadSession();
  }, []);

  async function handleLogin(email: string, password: string): Promise<void> {
    const tokenResponse = await apiPost<TokenResponse>("/auth/login", {
      email,
      password,
    });

    setAccessToken(tokenResponse.access_token);

    try {
      const currentUser = await apiGet<AuthenticatedUser>("/auth/me");
      setUser(currentUser);
    } catch (error) {
      clearAccessToken();
      throw error;
    }
  }

  function handleLogout() {
    clearAccessToken();
    setUser(null);
    setIsMenuOpen(false);
  }

  if (isAuthRequired && isAuthLoading) {
    return (
      <main className="login-page">
        <p>Verificando sesión...</p>
      </main>
    );
  }

  if (isAuthRequired && !user) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  const hasFinancialAccess = !isAuthRequired || user?.role !== "operator";
  const isAdministrator = user?.role === "admin";

  return (
    <AuthProvider user={user}>
      <div className="app-shell">
        <header className="topbar">
          <div className="topbar-brand">
            <div>
              <p className="brand">BrewMaster ERP</p>
              <p className="subtitle">Panel operativo</p>
            </div>

            {isAuthRequired && user && (
              <div className="session-controls">
                <span>{user.full_name}</span>
                <button
                  className="logout-button"
                  onClick={handleLogout}
                  type="button"
                >
                  Salir
                </button>
              </div>
            )}

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

            {hasFinancialAccess && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/insumos"
              >
                Insumos
              </NavLink>
            )}

            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              to="/producto-terminado"
            >
              Producto terminado
            </NavLink>

            {hasFinancialAccess && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/ventas"
              >
                Ventas
              </NavLink>
            )}

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

            {hasFinancialAccess && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/movimientos-insumos"
              >
                Mov. insumos
              </NavLink>
            )}

            {hasFinancialAccess && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/clientes"
              >
                Clientes
              </NavLink>
            )}

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

            {hasFinancialAccess && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/proveedores"
              >
                Proveedores
              </NavLink>
            )}

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

            {isAdministrator && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/usuarios"
              >
                Usuarios
              </NavLink>
            )}

            {hasFinancialAccess && (
              <NavLink
                className={({ isActive }) =>
                  isActive ? "nav-link active" : "nav-link"
                }
                to="/detalle-ventas"
              >
                Detalle ventas
              </NavLink>
            )}
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
          <Route path="/login" element={<Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route
            path="/usuarios"
            element={
              isAdministrator ? <UsersPage /> : <Navigate to="/" replace />
            }
          />
        </Routes>
      </div>
    </AuthProvider>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
