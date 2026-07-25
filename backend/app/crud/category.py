from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session):
    return db.query(Category).filter(Category.active.is_(True)).all()


def get_category_by_name(db: Session, category_name: str) -> Category | None:
    return db.query(Category).filter(Category.name == category_name).first()


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
