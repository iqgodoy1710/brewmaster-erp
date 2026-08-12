# BrewMaster ERP

Sistema MVP para gestionar una cervecería: inventario de insumos, recetas,
producción, envasado, stock de producto terminado, clientes y ventas.

## Funcionalidades

- Catálogos de cervezas, formatos, presentaciones, categorías y unidades.
- Insumos, proveedores y movimientos de stock.
- Recetas e ingredientes.
- Lotes de producción y consumo de materias primas.
- Corridas de envasado y consumo de materiales de envase.
- Stock y alertas de productos terminados.
- Clientes, ventas, cancelaciones y detalle de ventas.
- Panel operativo con alertas y ventas completadas.

## Requisitos

- Python 3.13 o compatible.
- Node.js 20 o superior.
- PostgreSQL.
- Git.

## Backend

Desde la raíz del proyecto:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configurá las variables necesarias en el archivo de entorno del backend. Como
mínimo:

```env
DATABASE_URL=postgresql://USUARIO:CONTRASENA@localhost:5432/brewmaster_erp
TEST_DATABASE_URL=postgresql://USUARIO:CONTRASENA@localhost:5432/brewmaster_erp_test
```

Aplicá las migraciones:

```powershell
alembic upgrade head
```

Iniciá la API:

```powershell
uvicorn app.main:app --reload
```

La documentación interactiva estará disponible en:

```text
http://127.0.0.1:8000/docs
```


## Frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
npm install
```

Creá `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Iniciá el frontend:

```powershell
npm run dev
```

La aplicación estará disponible en:

```text
http://localhost:5173
```

Para generar una compilación de producción:

```powershell
npm run build
```

## Tests

Con el entorno virtual del backend activo:

```powershell
cd backend
pytest -q
```

Actualmente la suite contiene 73 pruebas.

## Flujo operativo principal

1. Crear categorías, unidades, proveedores e insumos.
2. Registrar compras o saldos iniciales de insumos.
3. Crear cervezas, recetas e ingredientes.
4. Crear y completar un lote de producción.
5. Crear formatos, presentaciones y materiales de envasado.
6. Registrar una corrida de envasado.
7. Crear clientes y ventas.
8. Completar o cancelar ventas según corresponda.
9. Consultar el panel operativo y las alertas de stock.

## Variables de entorno

No incluir archivos `.env` o `.env.local` con credenciales en el repositorio.
Usá valores locales propios para desarrollo y pruebas.