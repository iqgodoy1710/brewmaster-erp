from sqlalchemy.orm import Session

from app.common.exceptions import (
    BeerPresentationNotFoundError,
    InactiveBeerPresentationError,
    InvalidSaleStatusError,
    SaleItemAlreadyExistsError,
    SaleNotFoundError,
)
from app.crud.beer_presentation import get_beer_presentation_by_id
from app.crud.sale import get_sale_by_id
from app.crud.sale_item import (
    create_sale_item,
    get_sale_item_by_sale_id_and_beer_presentation_id,
    get_sale_items,
)
from app.models.enums import SaleStatus
from app.schemas.sale_item import SaleItemCreate


class SaleItemService:
    @staticmethod
    def get_all_by_sale(
        db: Session,
        sale_id: int,
    ):
        sale = get_sale_by_id(db, sale_id)
        if not sale:
            raise SaleNotFoundError("The sale does not exist.")

        return get_sale_items(db, sale_id)

    @staticmethod
    def create(
        db: Session,
        sale_item_data: SaleItemCreate,
    ):
        sale = get_sale_by_id(db, sale_item_data.sale_id)
        if not sale:
            raise SaleNotFoundError("The sale does not exist.")

        if not sale.active or sale.status != SaleStatus.DRAFT:
            raise InvalidSaleStatusError(
                "Items can only be added to draft sales."
            )

        beer_presentation = get_beer_presentation_by_id(
            db,
            sale_item_data.beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError(
                "The beer presentation does not exist."
            )

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot add an inactive beer presentation to a sale."
            )

        existing_sale_item = (
            get_sale_item_by_sale_id_and_beer_presentation_id(
                db,
                sale_item_data.sale_id,
                sale_item_data.beer_presentation_id,
            )
        )
        if existing_sale_item:
            raise SaleItemAlreadyExistsError(
                "This beer presentation is already an item of the sale."
            )

        return create_sale_item(db, sale_item_data)