from app.common.exceptions import CategoryNameAlreadyExistsError
from app.crud.category import (
    create_category,
    get_categories,
    get_category_by_name,
)
from app.schemas.category import CategoryCreate
from sqlalchemy.orm import Session


class CategoryService:
    @staticmethod
    def get_all(db: Session):
        return get_categories(db)

    @staticmethod
    def create(db: Session, category_data: CategoryCreate):
        existing_category = get_category_by_name(db, category_data.name)

        if existing_category:
            raise CategoryNameAlreadyExistsError(
                "A category with this name already exists."
            )

        return create_category(db, category_data)
