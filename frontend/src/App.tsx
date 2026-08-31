import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Navigate,
  NavLink,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";

import "./App.css";
import { AuthProvider } from "./lib/auth";
import {
  apiGet,
  apiPost,
  clearAccessToken,
  getAccessToken,
  isDemoMode,
  isAuthRequired,
  setAccessToken,
} from "./lib/api";
import type { AuthenticatedUser, TokenResponse } from "./types/api";

import DashboardPage from "./pages/DashboardPage";
import RawMaterialsPage from "./pages/RawMaterialsPage";
import FinishedProductsPage from "./pages/FinishedProductsPage";
import SalesPage from "./pages/SalesPage";
import ProductionPage from "./pages/ProductionPage";

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
import UsersPage from "./pages/UsersPage";
import PricesPage from "./pages/PricesPage";
import CostCalculatorPage from "./pages/CostCalculatorPage";
import CustomerAccountsPage from "./pages/CustomerAccountsPage";
import KegsPage from "./pages/KegsPage";
import KegQrPage from "./pages/KegQrPage";
import KegQrLabelPage from "./pages/KegQrLabelPage";
import KegQrLabelsPage from "./pages/KegQrLabelsPage";
import KegRepackagingPage from "./pages/KegRepackagingPage";

function AppContent() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isSessionLoading, setIsSessionLoading] = useState(isAuthRequired);
  const location = useLocation();

  useEffect(() => {
    async function loadSession() {
      if (!isAuthRequired || !getAccessToken()) {
        setIsSessionLoading(false);
        return;
      }

      try {
        const currentUser = await apiGet<AuthenticatedUser>("/auth/me");
        setUser(currentUser);
      } catch {
        clearAccessToken();
        setUser(null);
      } finally {
        setIsSessionLoading(false);
      }
    }

    void loadSession();
  }, []);

  async function handleLogin(
    username: string,
    password: string,
  ): Promise<void> {
    const tokenResponse = await apiPost<TokenResponse>(
      "/auth/login",
      {
        username,
        password,
      },
      {
        retryOnTemporaryFailure: true,
      },
    );

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

  if (isAuthRequired && isSessionLoading) {
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
        <Route
          path="*"
          element={
            <Navigate
              replace
              state={{
                from: {
                  pathname: location.pathname,
                  search: location.search,
                  hash: location.hash,
                },
              }}
              to="/login"
            />
          }
        />
      </Routes>
    );
  }

  const isAdministrator = !isAuthRequired || user?.role === "admin";

  const isOperator = user?.role === "operator";

  const isManagement = user?.role === "management";

  const hasFinancialAccess = !isAuthRequired || isAdministrator || isManagement;

  const canOperate = !isAuthRequired || isAdministrator || isOperator;

  const canViewKegs =
    !isAuthRequired || isAdministrator || isOperator || isManagement;

  const canManageCatalogs = !isAuthRequired || isAdministrator || isOperator;

  const canViewFinishedProducts =
    !isAuthRequired || isAdministrator || isOperator || isManagement;

  function closeMenu() {
    setIsMenuOpen(false);
  }

  const loginRedirectState = location.state as {
    from?: {
      pathname?: string;
      search?: string;
      hash?: string;
    };
  } | null;

  const loginRedirectPath = loginRedirectState?.from
    ? `${loginRedirectState.from.pathname ?? "/"}${
        loginRedirectState.from.search ?? ""
      }${loginRedirectState.from.hash ?? ""}`
    : "/";

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
            onClick={(event) => {
              if ((event.target as HTMLElement).closest("a")) {
                setIsMenuOpen(false);

                event.currentTarget
                  .querySelectorAll("details[open]")
                  .forEach((group) => group.removeAttribute("open"));
              }
            }}
          >
            <NavLink
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
              end
              to="/"
              onClick={closeMenu}
            >
              Dashboard
            </NavLink>

            {(canOperate || canViewFinishedProducts || hasFinancialAccess) && (
              <details className="nav-group">
                <summary>Operación</summary>

                <div className="nav-group-menu">
                  {hasFinancialAccess && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/movimientos-insumos"
                      onClick={closeMenu}
                    >
                      Mov. insumos
                    </NavLink>
                  )}

                  {canOperate && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/produccion"
                      onClick={closeMenu}
                    >
                      Producción
                    </NavLink>
                  )}

                  {canViewKegs && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/embotellado"
                      onClick={closeMenu}
                    >
                      Embotellado
                    </NavLink>
                  )}

                  {canViewKegs && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/barriles"
                      onClick={closeMenu}
                    >
                      Barriles
                    </NavLink>
                  )}
                </div>
              </details>
            )}

            {hasFinancialAccess && (
              <details className="nav-group">
                <summary>Comercial</summary>

                <div className="nav-group-menu">
                  <NavLink
                    className={({ isActive }) =>
                      isActive ? "nav-link active" : "nav-link"
                    }
                    to="/cuentas-corrientes"
                    onClick={closeMenu}
                  >
                    Ctas. corrientes
                  </NavLink>

                  <NavLink
                    className={({ isActive }) =>
                      isActive ? "nav-link active" : "nav-link"
                    }
                    to="/ventas"
                    onClick={closeMenu}
                  >
                    Ventas
                  </NavLink>

                  <NavLink
                    className={({ isActive }) =>
                      isActive ? "nav-link active" : "nav-link"
                    }
                    to="/detalle-ventas"
                    onClick={closeMenu}
                  >
                    Detalle ventas
                  </NavLink>

                  <NavLink
                    className={({ isActive }) =>
                      isActive ? "nav-link active" : "nav-link"
                    }
                    to="/precios"
                    onClick={closeMenu}
                  >
                    Precios
                  </NavLink>

                  <NavLink
                    className={({ isActive }) =>
                      isActive ? "nav-link active" : "nav-link"
                    }
                    to="/costos"
                    onClick={closeMenu}
                  >
                    Costos
                  </NavLink>
                </div>
              </details>
            )}

            {(canManageCatalogs ||
              hasFinancialAccess ||
              canViewFinishedProducts) && (
              <details className="nav-group">
                <summary>Configuración</summary>

                <div className="nav-group-menu">
                  {hasFinancialAccess && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/clientes"
                      onClick={closeMenu}
                    >
                      Clientes
                    </NavLink>
                  )}

                  {canViewFinishedProducts && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/producto-terminado"
                      onClick={closeMenu}
                    >
                      Producto terminado
                    </NavLink>
                  )}

                  {hasFinancialAccess && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/insumos"
                      onClick={closeMenu}
                    >
                      Insumos
                    </NavLink>
                  )}

                  {canManageCatalogs && (
                    <>
                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/cervezas"
                        onClick={closeMenu}
                      >
                        Cervezas
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/formatos-envasado"
                        onClick={closeMenu}
                      >
                        Formatos
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/presentaciones"
                        onClick={closeMenu}
                      >
                        Presentaciones
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/recetas"
                        onClick={closeMenu}
                      >
                        Recetas
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/ingredientes-receta"
                        onClick={closeMenu}
                      >
                        Ingredientes
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/materiales-envasado"
                        onClick={closeMenu}
                      >
                        Materiales
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/categorias"
                        onClick={closeMenu}
                      >
                        Categorías
                      </NavLink>

                      <NavLink
                        className={({ isActive }) =>
                          isActive ? "nav-link active" : "nav-link"
                        }
                        to="/unidades"
                        onClick={closeMenu}
                      >
                        Unidades
                      </NavLink>
                    </>
                  )}

                  {hasFinancialAccess && (
                    <NavLink
                      className={({ isActive }) =>
                        isActive ? "nav-link active" : "nav-link"
                      }
                      to="/proveedores"
                      onClick={closeMenu}
                    >
                      Proveedores
                    </NavLink>
                  )}
                </div>
              </details>
            )}

            {isAdministrator && (
              <details className="nav-group">
                <summary>Administración</summary>

                <div className="nav-group-menu">
                  <NavLink
                    className={({ isActive }) =>
                      isActive ? "nav-link active" : "nav-link"
                    }
                    to="/usuarios"
                    onClick={closeMenu}
                  >
                    Usuarios
                  </NavLink>
                </div>
              </details>
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

          <Route
            path="/insumos"
            element={
              hasFinancialAccess ? (
                <RawMaterialsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/producto-terminado"
            element={
              canViewFinishedProducts ? (
                <FinishedProductsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/ventas"
            element={
              hasFinancialAccess ? <SalesPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/precios"
            element={
              hasFinancialAccess ? <PricesPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/costos"
            element={
              hasFinancialAccess ? (
                <CostCalculatorPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/produccion"
            element={
              canOperate ? <ProductionPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/embotellado"
            element={
              canViewKegs ? <KegRepackagingPage /> : <Navigate to="/" replace />
            }
          />
          <Route
            path="/barriles/qr/:code"
            element={canViewKegs ? <KegQrPage /> : <Navigate to="/" replace />}
          />

          <Route
            path="/barriles/etiqueta/:code"
            element={
              canOperate ? <KegQrLabelPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/barriles/etiquetas"
            element={
              canOperate ? <KegQrLabelsPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/barriles"
            element={canViewKegs ? <KegsPage /> : <Navigate to="/" replace />}
          />

          <Route
            path="/movimientos-insumos"
            element={
              hasFinancialAccess ? (
                <RawMaterialMovementsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/clientes"
            element={
              hasFinancialAccess ? (
                <CustomersPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/cuentas-corrientes"
            element={
              hasFinancialAccess ? (
                <CustomerAccountsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/detalle-ventas"
            element={
              hasFinancialAccess ? (
                <SaleDetailsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/proveedores"
            element={
              hasFinancialAccess ? (
                <SuppliersPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/cervezas"
            element={
              canManageCatalogs ? <BeersPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/formatos-envasado"
            element={
              canManageCatalogs ? (
                <PackagingFormatsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/presentaciones"
            element={
              canManageCatalogs ? (
                <BeerPresentationsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/recetas"
            element={
              canManageCatalogs ? <RecipesPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/ingredientes-receta"
            element={
              canManageCatalogs ? (
                <RecipeIngredientsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/materiales-envasado"
            element={
              canManageCatalogs ? (
                <BeerPresentationPackagingMaterialsPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/categorias"
            element={
              canManageCatalogs ? (
                <CategoriesPage />
              ) : (
                <Navigate to="/" replace />
              )
            }
          />

          <Route
            path="/unidades"
            element={
              canManageCatalogs ? <UnitsPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/usuarios"
            element={
              isAdministrator ? <UsersPage /> : <Navigate to="/" replace />
            }
          />

          <Route
            path="/login"
            element={<Navigate to={loginRedirectPath} replace />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
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
