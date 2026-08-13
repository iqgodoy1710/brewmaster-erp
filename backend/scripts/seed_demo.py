import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

database_url = os.getenv("DATABASE_URL", "")
database_name = urlparse(database_url).path.lstrip("/")

if os.getenv("DEMO_SEED_ALLOWED") != "true":
    raise RuntimeError(
        "Set DEMO_SEED_ALLOWED=true before running this script."
    )

if database_name != "brewmaster_demo":
    raise RuntimeError(
        "This script only runs against the brewmaster_demo database."
    )

from app.db.database import SessionLocal
from app.models.beer import Beer
from app.models.beer_presentation import BeerPresentation
from app.models.beer_presentation_packaging_material import (
    BeerPresentationPackagingMaterial,
)
from app.models.beer_presentation_stock_movement import (
    BeerPresentationStockMovement,
)
from app.models.category import Category
from app.models.customer import Customer
from app.models.enums import (
    BeerPresentationStockMovementType,
    ProductionBatchStatus,
    RawMaterialMovementType,
    SaleStatus,
)
from app.models.packaging_format import PackagingFormat
from app.models.packaging_run import PackagingRun
from app.models.production_batch import ProductionBatch
from app.models.raw_material import RawMaterial
from app.models.raw_material_stock_movement import RawMaterialStockMovement
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.supplier import Supplier
from app.models.unit import Unit


def get_or_create(db, model, lookup, values):
    instance = db.query(model).filter_by(**lookup).one_or_none()

    if instance is None:
        instance = model(**lookup, **values)
        db.add(instance)
        db.flush()

    return instance


def ensure_raw_material_movement(
    db,
    raw_material,
    movement_type,
    quantity,
    reference,
    occurred_at,
    supplier=None,
    unit_cost=None,
    production_batch=None,
    packaging_run=None,
    notes=None,
):
    movement = (
        db.query(RawMaterialStockMovement)
        .filter_by(
            raw_material_id=raw_material.id,
            movement_type=movement_type,
            reference=reference,
        )
        .one_or_none()
    )

    if movement is None:
        movement = RawMaterialStockMovement(
            raw_material_id=raw_material.id,
            production_batch_id=(
                production_batch.id if production_batch else None
            ),
            packaging_run_id=packaging_run.id if packaging_run else None,
            supplier_id=supplier.id if supplier else None,
            movement_type=movement_type,
            quantity=quantity,
            unit_cost=unit_cost,
            reference=reference,
            notes=notes,
            occurred_at=occurred_at,
        )
        db.add(movement)


def ensure_presentation_movement(
    db,
    presentation,
    movement_type,
    quantity,
    reference,
    occurred_at,
    packaging_run=None,
    sale=None,
    notes=None,
):
    movement = (
        db.query(BeerPresentationStockMovement)
        .filter_by(
            beer_presentation_id=presentation.id,
            movement_type=movement_type,
            reference=reference,
        )
        .one_or_none()
    )

    if movement is None:
        movement = BeerPresentationStockMovement(
            beer_presentation_id=presentation.id,
            packaging_run_id=packaging_run.id if packaging_run else None,
            sale_id=sale.id if sale else None,
            movement_type=movement_type,
            quantity=quantity,
            reference=reference,
            notes=notes,
            occurred_at=occurred_at,
        )
        db.add(movement)


def main():
    db = SessionLocal()

    try:
        receipt_date = datetime(2026, 8, 1, 9, 0)
        production_date = datetime(2026, 8, 10, 10, 0)
        packaging_date = datetime(2026, 8, 11, 11, 0)
        sale_date = datetime(2026, 8, 12, 16, 0)

        categories = {
            name: get_or_create(
                db,
                Category,
                {"name": name},
                {"description": description},
            )
            for name, description in [
                ("Maltas", "Maltas base y especiales para elaboración."),
                ("Lúpulos", "Lúpulos para amargor y aroma."),
                ("Levaduras", "Levaduras para fermentación."),
                ("Envases", "Botellas, tapas y etiquetas."),
            ]
        }

        units = {
            symbol: get_or_create(
                db,
                Unit,
                {"symbol": symbol},
                {"name": name},
            )
            for name, symbol in [
                ("Kilogramo", "kg"),
                ("Unidad", "un"),
            ]
        }

        malt_supplier = get_or_create(
            db,
            Supplier,
            {"tax_id": "DEMO-MALT-001"},
            {
                "name": "Maltería Demo",
                "email": "ventas@malteria-demo.test",
                "phone": "+54 11 5555 0101",
            },
        )

        packaging_supplier = get_or_create(
            db,
            Supplier,
            {"tax_id": "DEMO-ENV-001"},
            {
                "name": "Envases Demo",
                "email": "ventas@envases-demo.test",
                "phone": "+54 11 5555 0102",
            },
        )

        raw_material_specs = [
            (
                "MALT-PALE-DEMO",
                "Malta Pale Ale",
                "Maltas",
                "kg",
                Decimal("250.000"),
                Decimal("100.000"),
                Decimal("2.50"),
                "Malta base para cervezas ale.",
            ),
            (
                "HOP-CASCADE-DEMO",
                "Lúpulo Cascade",
                "Lúpulos",
                "kg",
                Decimal("1.200"),
                Decimal("2.000"),
                Decimal("18.00"),
                "Lúpulo cítrico para aroma y amargor.",
            ),
            (
                "YEAST-US05-DEMO",
                "Levadura US-05",
                "Levaduras",
                "kg",
                Decimal("0.500"),
                Decimal("1.000"),
                Decimal("35.00"),
                "Levadura seca para cervezas ale.",
            ),
            (
                "BOTTLE-500-DEMO",
                "Botella ámbar 500 ml",
                "Envases",
                "un",
                Decimal("1980.000"),
                Decimal("500.000"),
                Decimal("0.35"),
                "Botella de vidrio para cerveza.",
            ),
            (
                "CAP-CROWN-DEMO",
                "Tapa corona",
                "Envases",
                "un",
                Decimal("1980.000"),
                Decimal("500.000"),
                Decimal("0.08"),
                "Tapa corona estándar.",
            ),
            (
                "LABEL-IPA-DEMO",
                "Etiqueta IPA 500 ml",
                "Envases",
                "un",
                Decimal("1980.000"),
                Decimal("500.000"),
                Decimal("0.12"),
                "Etiqueta para botella de IPA.",
            ),
        ]

        raw_materials = {}

        for (
            code,
            name,
            category_name,
            unit_symbol,
            current_stock,
            minimum_stock,
            current_cost,
            description,
        ) in raw_material_specs:
            raw_materials[code] = get_or_create(
                db,
                RawMaterial,
                {"code": code},
                {
                    "name": name,
                    "category_id": categories[category_name].id,
                    "unit_id": units[unit_symbol].id,
                    "current_stock": current_stock,
                    "minimum_stock": minimum_stock,
                    "current_cost": current_cost,
                    "description": description,
                },
            )

        ipa = get_or_create(
            db,
            Beer,
            {"code": "IPA-DEMO"},
            {
                "name": "IPA Demo",
                "style": "India Pale Ale",
                "description": "Cerveza de ejemplo para la demo pública.",
            },
        )

        recipe = get_or_create(
            db,
            Recipe,
            {"beer_id": ipa.id, "version": 1},
            {
                "target_volume_liters": Decimal("500.000"),
                "notes": "Receta demo para un lote de 500 litros.",
            },
        )

        for raw_material_code, required_quantity in [
            ("MALT-PALE-DEMO", Decimal("100.000")),
            ("HOP-CASCADE-DEMO", Decimal("1.800")),
            ("YEAST-US05-DEMO", Decimal("1.000")),
        ]:
            get_or_create(
                db,
                RecipeIngredient,
                {
                    "recipe_id": recipe.id,
                    "raw_material_id": raw_materials[raw_material_code].id,
                },
                {"required_quantity": required_quantity},
            )

        bottle_format = get_or_create(
            db,
            PackagingFormat,
            {"code": "BOTTLE-500-DEMO"},
            {
                "name": "Botella 500 ml",
                "capacity_liters": Decimal("0.500"),
                "description": "Formato demo de botella retornable.",
            },
        )

        presentation = get_or_create(
            db,
            BeerPresentation,
            {"code": "IPA-BOTTLE-500-DEMO"},
            {
                "name": "IPA Demo botella 500 ml",
                "beer_id": ipa.id,
                "packaging_format_id": bottle_format.id,
                "current_stock": 14,
                "minimum_stock": 24,
                "description": "Presentación demo para venta minorista.",
            },
        )

        for raw_material_code in [
            "BOTTLE-500-DEMO",
            "CAP-CROWN-DEMO",
            "LABEL-IPA-DEMO",
        ]:
            get_or_create(
                db,
                BeerPresentationPackagingMaterial,
                {
                    "beer_presentation_id": presentation.id,
                    "raw_material_id": raw_materials[raw_material_code].id,
                },
                {"required_quantity": Decimal("1.000")},
            )

        completed_batch = get_or_create(
            db,
            ProductionBatch,
            {"code": "PB-IPA-DEMO-001"},
            {
                "recipe_id": recipe.id,
                "planned_volume_liters": Decimal("500.000"),
                "produced_volume_liters": Decimal("500.000"),
                "available_bulk_volume_liters": Decimal("490.000"),
                "status": ProductionBatchStatus.COMPLETED,
                "completed_at": production_date,
                "notes": "Lote demo completado.",
            },
        )

        get_or_create(
            db,
            ProductionBatch,
            {"code": "PB-IPA-DEMO-002"},
            {
                "recipe_id": recipe.id,
                "planned_volume_liters": Decimal("500.000"),
                "available_bulk_volume_liters": Decimal("0.000"),
                "status": ProductionBatchStatus.PLANNED,
                "notes": "Lote demo planificado.",
            },
        )

        packaging_run = get_or_create(
            db,
            PackagingRun,
            {"code": "PACK-IPA-DEMO-001"},
            {
                "production_batch_id": completed_batch.id,
                "beer_presentation_id": presentation.id,
                "packaged_quantity": 20,
                "packaged_volume_liters": Decimal("10.000"),
                "occurred_at": packaging_date,
                "notes": "Corrida demo de envasado.",
            },
        )

        customer = get_or_create(
            db,
            Customer,
            {"code": "CLIENT-DEMO-001"},
            {
                "name": "Cervecería Amiga Demo",
                "tax_id": "DEMO-CUSTOMER-001",
                "email": "compras@cerveceria-demo.test",
                "phone": "+54 11 5555 0201",
                "address": "Av. Demo 123, Buenos Aires",
            },
        )

        sale = get_or_create(
            db,
            Sale,
            {"code": "SALE-DEMO-001"},
            {
                "customer_id": customer.id,
                "status": SaleStatus.COMPLETED,
                "completed_at": sale_date,
                "notes": "Venta demo de producto terminado.",
            },
        )

        get_or_create(
            db,
            SaleItem,
            {
                "sale_id": sale.id,
                "beer_presentation_id": presentation.id,
            },
            {
                "quantity": 6,
                "unit_price": Decimal("7.00"),
            },
        )

        receipt_quantities = {
            "MALT-PALE-DEMO": Decimal("350.000"),
            "HOP-CASCADE-DEMO": Decimal("3.000"),
            "YEAST-US05-DEMO": Decimal("1.500"),
            "BOTTLE-500-DEMO": Decimal("2000.000"),
            "CAP-CROWN-DEMO": Decimal("2000.000"),
            "LABEL-IPA-DEMO": Decimal("2000.000"),
        }

        for raw_material_code, quantity in receipt_quantities.items():
            supplier = (
                packaging_supplier
                if raw_material_code.endswith("DEMO")
                and raw_material_code.startswith(
                    ("BOTTLE", "CAP", "LABEL")
                )
                else malt_supplier
            )

            ensure_raw_material_movement(
                db,
                raw_materials[raw_material_code],
                RawMaterialMovementType.PURCHASE_RECEIPT,
                quantity,
                f"PURCHASE-{raw_material_code}",
                receipt_date,
                supplier=supplier,
                unit_cost=raw_materials[raw_material_code].current_cost,
                notes="Ingreso inicial para la demo.",
            )

        for raw_material_code, quantity in [
            ("MALT-PALE-DEMO", Decimal("100.000")),
            ("HOP-CASCADE-DEMO", Decimal("1.800")),
            ("YEAST-US05-DEMO", Decimal("1.000")),
        ]:
            ensure_raw_material_movement(
                db,
                raw_materials[raw_material_code],
                RawMaterialMovementType.PRODUCTION_CONSUMPTION,
                quantity,
                completed_batch.code,
                production_date,
                production_batch=completed_batch,
                notes="Consumo de insumo durante producción demo.",
            )

        for raw_material_code in [
            "BOTTLE-500-DEMO",
            "CAP-CROWN-DEMO",
            "LABEL-IPA-DEMO",
        ]:
            ensure_raw_material_movement(
                db,
                raw_materials[raw_material_code],
                RawMaterialMovementType.PRODUCTION_CONSUMPTION,
                Decimal("20.000"),
                packaging_run.code,
                packaging_date,
                packaging_run=packaging_run,
                notes="Consumo de material durante envasado demo.",
            )

        ensure_presentation_movement(
            db,
            presentation,
            BeerPresentationStockMovementType.PACKAGING_RECEIPT,
            20,
            packaging_run.code,
            packaging_date,
            packaging_run=packaging_run,
            notes="Ingreso de producto terminado por envasado demo.",
        )

        ensure_presentation_movement(
            db,
            presentation,
            BeerPresentationStockMovementType.SALE,
            6,
            sale.code,
            sale_date,
            sale=sale,
            notes="Salida de producto terminado por venta demo.",
        )

        db.commit()

        print("Demo data loaded successfully.")
        print("Beer: IPA-DEMO")
        print("Completed batch: PB-IPA-DEMO-001")
        print("Packaging run: PACK-IPA-DEMO-001")
        print("Completed sale: SALE-DEMO-001")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()