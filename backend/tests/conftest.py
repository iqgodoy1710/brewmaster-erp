import pytest
from app.core.config import TEST_DATABASE_URL
from app.db.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL must be configured to run tests.")


test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def clean_database():
    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE "
                "raw_materials, raw_material_categories, units, suppliers, "
                "raw_material_stock_movements, beers, recipes, recipe_ingredients, "
                "production_batches, packaging_formats, kegs, keg_movements, beer_presentations, "
                "keg_repackaging_runs, beer_presentation_packaging_materials, packaging_runs, "
                "beer_presentation_stock_movements, customers, sales, sale_items, users, "
                "code_sequences, beer_presentation_prices, "
                "customer_payments, customer_account_movements "
                "RESTART IDENTITY CASCADE"
            )
        )

    yield

    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE "
                "raw_materials, raw_material_categories, units, suppliers, "
                "raw_material_stock_movements, beers, recipes, recipe_ingredients, "
                "production_batches, packaging_formats, kegs, keg_movements, beer_presentations, "
                "keg_repackaging_runs, beer_presentation_packaging_materials, packaging_runs, "
                "beer_presentation_stock_movements, customers, sales, sale_items, users, "
                "code_sequences, beer_presentation_prices, "
                "customer_payments, customer_account_movements "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
