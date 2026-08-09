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

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <header className="topbar">
          <div>
            <p className="brand">BrewMaster ERP</p>
            <p className="subtitle">Panel operativo</p>
          </div>

          <nav className="navigation" aria-label="Navegación principal">
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
          </nav>
        </header>

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
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
