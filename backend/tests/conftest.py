import pytest
from app.core.config import TEST_DATABASE_URL
from app.db.dependencies import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

if TEST_DATABASE_URL is None:
    raise RuntimeError(
        "TEST_DATABASE_URL must be configured to run tests."
    )


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
                "raw_materials, raw_material_categories, units, suppliers "
                "RESTART IDENTITY CASCADE"
            )
        )

    yield

    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE "
                "raw_materials, raw_material_categories, units "
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