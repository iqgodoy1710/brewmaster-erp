from decimal import Decimal

from app.common.exceptions import (
    BeerPresentationNotFoundError,
    CustomerNotFoundError,
    InactiveBeerPresentationError,
    InactiveCustomerError,
    InsufficientBeerPresentationStockError,
    InvalidSaleStatusError,
    SaleCodeAlreadyExistsError,
    SaleHasNoItemsError,
    SaleNotFoundError,
)
from app.crud.beer_presentation import (
    get_beer_presentation_by_id,
    update_beer_presentation_stock,
)
from app.crud.beer_presentation_stock_movement import (
    create_sale_cancellation_movement,
    create_sale_movement,
)
from app.crud.customer import get_customer_by_id
from app.crud.sale import (
    cancel_sale,
    complete_sale,
    create_sale,
    get_sale_by_code,
    get_sale_detail_by_code,
    get_sales,
)
from app.crud.sale_item import get_sale_items
from app.models.enums import SaleStatus
from app.schemas.sale import SaleCancel, SaleCreate
from app.schemas.sale_detail import (
    SaleDetailItemResponse,
    SaleDetailResponse,
)
from sqlalchemy.orm import Session


class SaleService:
    @staticmethod
    def get_all(db: Session):
        return get_sales(db)

    @staticmethod
    def create(
        db: Session,
        sale_data: SaleCreate,
    ):
        customer = get_customer_by_id(
            db,
            sale_data.customer_id,
        )
        if not customer:
            raise CustomerNotFoundError("The customer does not exist.")

        if not customer.active:
            raise InactiveCustomerError(
                "Cannot create a sale for an inactive customer."
            )

        existing_sale = get_sale_by_code(
            db,
            sale_data.code,
        )
        if existing_sale:
            raise SaleCodeAlreadyExistsError("A sale with this code already exists.")

        return create_sale(db, sale_data)

    @staticmethod
    def complete(
        db: Session,
        code: str,
    ):
        sale = get_sale_by_code(db, code)
        if not sale:
            raise SaleNotFoundError("The sale does not exist.")

        if not sale.active or sale.status != SaleStatus.DRAFT:
            raise InvalidSaleStatusError("Only draft sales can be completed.")

        sale_items = get_sale_items(db, sale.id)
        if not sale_items:
            raise SaleHasNoItemsError("Cannot complete a sale without items.")

        presentation_sales = []

        for sale_item in sale_items:
            beer_presentation = get_beer_presentation_by_id(
                db,
                sale_item.beer_presentation_id,
            )
            if not beer_presentation:
                raise BeerPresentationNotFoundError(
                    "A beer presentation does not exist."
                )

            if not beer_presentation.active:
                raise InactiveBeerPresentationError(
                    "Cannot sell an inactive beer presentation."
                )

            if beer_presentation.current_stock < sale_item.quantity:
                raise InsufficientBeerPresentationStockError(
                    "There is not enough stock for a beer presentation."
                )

            presentation_sales.append((beer_presentation, sale_item.quantity))

        try:
            for beer_presentation, quantity in presentation_sales:
                create_sale_movement(
                    db,
                    beer_presentation_id=beer_presentation.id,
                    sale_id=sale.id,
                    quantity=quantity,
                    reference=sale.code,
                    notes=f"Stock output for sale {sale.code}.",
                )
                update_beer_presentation_stock(
                    db,
                    beer_presentation,
                    beer_presentation.current_stock - quantity,
                )

            complete_sale(db, sale)
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(sale)

        return sale

    @staticmethod
    def cancel(
        db: Session,
        code: str,
        cancellation_data: SaleCancel,
    ):
        sale = get_sale_by_code(db, code)
        if not sale:
            raise SaleNotFoundError("The sale does not exist.")

        if not sale.active or sale.status not in {
            SaleStatus.DRAFT,
            SaleStatus.COMPLETED,
        }:
            raise InvalidSaleStatusError(
                "Only draft or completed sales can be cancelled."
            )

        if sale.status == SaleStatus.DRAFT:
            try:
                cancel_sale(
                    db,
                    sale,
                    cancellation_data.cancellation_reason,
                )
                db.commit()
            except Exception:
                db.rollback()
                raise

            db.refresh(sale)

            return sale

        sale_items = get_sale_items(db, sale.id)
        if not sale_items:
            raise SaleHasNoItemsError("Cannot cancel a completed sale without items.")

        presentation_returns = []

        for sale_item in sale_items:
            beer_presentation = get_beer_presentation_by_id(
                db,
                sale_item.beer_presentation_id,
            )
            if not beer_presentation:
                raise BeerPresentationNotFoundError(
                    "A beer presentation does not exist."
                )

            presentation_returns.append((beer_presentation, sale_item.quantity))

        try:
            for beer_presentation, quantity in presentation_returns:
                create_sale_cancellation_movement(
                    db,
                    beer_presentation_id=beer_presentation.id,
                    sale_id=sale.id,
                    quantity=quantity,
                    reference=sale.code,
                    notes=(f"Stock return for cancelled sale {sale.code}."),
                )
                update_beer_presentation_stock(
                    db,
                    beer_presentation,
                    beer_presentation.current_stock + quantity,
                )

            cancel_sale(
                db,
                sale,
                cancellation_data.cancellation_reason,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(sale)

        return sale

    @staticmethod
    def get_detail(
        db: Session,
        code: str,
    ) -> SaleDetailResponse:
        sale = get_sale_detail_by_code(db, code)

        if not sale:
            raise SaleNotFoundError("The sale does not exist.")

        items = [
            SaleDetailItemResponse(
                beer_presentation_id=item.beer_presentation.id,
                beer_presentation_code=item.beer_presentation.code,
                beer_presentation_name=item.beer_presentation.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.quantity * item.unit_price,
            )
            for item in sale.items
            if item.active
        ]

        total_amount = sum(
            (item.line_total for item in items),
            Decimal("0.00"),
        )

        return SaleDetailResponse(
            id=sale.id,
            code=sale.code,
            customer_id=sale.customer.id,
            customer_name=sale.customer.name,
            status=sale.status,
            notes=sale.notes,
            completed_at=sale.completed_at,
            cancelled_at=sale.cancelled_at,
            cancellation_reason=sale.cancellation_reason,
            created_at=sale.created_at,
            updated_at=sale.updated_at,
            items=items,
            total_amount=total_amount,
        )
