from decimal import Decimal

from app.common.exceptions import (
    BeerPresentationNotFoundError,
    CustomerNotFoundError,
    InactiveBeerPresentationError,
    InactiveCustomerError,
    InactiveKegError,
    InsufficientBeerPresentationStockError,
    InvalidKegDeliveryError,
    InvalidSaleStatusError,
    KegNotFoundError,
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
from app.crud.customer_account_movement import (
    create_customer_account_movement,
)
from app.crud.keg import (
    get_keg_by_id,
    update_keg_state,
)
from app.crud.keg_movement import create_keg_movement
from app.crud.packaging_format import get_packaging_format_by_id
from app.crud.sale import (
    cancel_sale,
    complete_sale,
    create_sale,
    get_completed_sales_report,
    get_sale_by_code,
    get_sale_detail_by_code,
    get_sales,
)
from app.crud.sale_item import get_sale_items
from app.models.enums import (
    CustomerAccountMovementType,
    KegMovementType,
    KegStatus,
    PackagingFormatType,
    SaleStatus,
)
from app.schemas.sale import (
    SaleCancel,
    SaleComplete,
    SaleCreate,
)
from app.schemas.sale_detail import (
    SaleDetailItemResponse,
    SaleDetailResponse,
)
from app.schemas.sale_report import SaleReportItemResponse
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class SaleService:
    @staticmethod
    def get_all(db: Session):
        return get_sales(db)

    @staticmethod
    def get_completed_report(
        db: Session,
    ) -> list[SaleReportItemResponse]:
        rows = get_completed_sales_report(db)

        return [
            SaleReportItemResponse(
                sale_id=row.sale_id,
                sale_code=row.sale_code,
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                completed_at=row.completed_at,
                total_units=row.total_units,
                total_amount=row.total_amount,
            )
            for row in rows
        ]

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

        return create_sale(
            db,
            sale_data,
            generate_code(db, "sale"),
        )

    @staticmethod
    def complete(
        db: Session,
        code: str,
        completion_data: SaleComplete | None = None,
    ):
        sale = get_sale_by_code(db, code)
        if not sale:
            raise SaleNotFoundError("The sale does not exist.")

        if not sale.active or sale.status != SaleStatus.DRAFT:
            raise InvalidSaleStatusError(
                "Only draft sales can be completed."
            )

        sale_items = get_sale_items(db, sale.id)
        if not sale_items:
            raise SaleHasNoItemsError(
                "Cannot complete a sale without items."
            )

        sale_total = sum(
            (
                sale_item.quantity * sale_item.unit_price
                for sale_item in sale_items
            ),
            Decimal("0.00"),
        )

        presentation_sales = []
        required_keg_quantities: dict[int, int] = {}

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

            packaging_format = get_packaging_format_by_id(
                db,
                beer_presentation.packaging_format_id,
            )
            if not packaging_format:
                raise InvalidKegDeliveryError(
                    "A beer presentation packaging format does not exist."
                )

            if packaging_format.format_type == PackagingFormatType.KEG:
                required_keg_quantities[beer_presentation.id] = (
                    sale_item.quantity
                )

            presentation_sales.append(
                (beer_presentation, sale_item.quantity)
            )

        keg_ids = (
            completion_data.keg_ids
            if completion_data is not None
            else []
        )

        if len(keg_ids) != len(set(keg_ids)):
            raise InvalidKegDeliveryError(
                "A keg can only be assigned once to a sale."
            )

        assigned_keg_quantities: dict[int, int] = {}
        kegs_to_deliver = []

        for keg_id in keg_ids:
            keg = get_keg_by_id(db, keg_id)

            if not keg:
                raise KegNotFoundError("The keg does not exist.")

            if not keg.active:
                raise InactiveKegError(
                    "Cannot deliver an inactive keg."
                )

            if keg.status != KegStatus.FILLED:
                raise InvalidKegDeliveryError(
                    "Only filled kegs can be delivered."
                )

            if (
                keg.beer_presentation_id
                not in required_keg_quantities
            ):
                raise InvalidKegDeliveryError(
                    "The keg beer presentation is not included in the sale."
                )

            assigned_keg_quantities[keg.beer_presentation_id] = (
                assigned_keg_quantities.get(
                    keg.beer_presentation_id,
                    0,
                )
                + 1
            )
            kegs_to_deliver.append(keg)

        if assigned_keg_quantities != required_keg_quantities:
            raise InvalidKegDeliveryError(
                "The assigned kegs do not match the keg quantities of the sale."
            )

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

            for keg in kegs_to_deliver:
                create_keg_movement(
                    db,
                    keg_id=keg.id,
                    movement_type=KegMovementType.DELIVERY,
                    previous_status=keg.status,
                    new_status=KegStatus.AT_CUSTOMER,
                    resulting_volume_liters=keg.current_volume_liters,
                    beer_presentation_id=keg.beer_presentation_id,
                    production_batch_id=keg.production_batch_id,
                    sale_id=sale.id,
                    customer_id=sale.customer_id,
                    reference=sale.code,
                    notes=(
                        f"Keg delivery for sale {sale.code}."
                    ),
                )

                update_keg_state(
                    db,
                    keg,
                    status=KegStatus.AT_CUSTOMER,
                    current_volume_liters=keg.current_volume_liters,
                    beer_presentation_id=keg.beer_presentation_id,
                    production_batch_id=keg.production_batch_id,
                    customer_id=sale.customer_id,
                )

            create_customer_account_movement(
                db,
                customer_id=sale.customer_id,
                sale_id=sale.id,
                movement_type=CustomerAccountMovementType.SALE_CHARGE,
                amount=sale_total,
                reference=sale.code,
                notes=f"Account charge for sale {sale.code}.",
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
        sale_total = sum(
            (sale_item.quantity * sale_item.unit_price for sale_item in sale_items),
            Decimal("0.00"),
        )

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
            create_customer_account_movement(
                db,
                customer_id=sale.customer_id,
                sale_id=sale.id,
                movement_type=(CustomerAccountMovementType.SALE_CANCELLATION),
                amount=sale_total,
                reference=sale.code,
                notes=(f"Account reversal for cancelled sale {sale.code}."),
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
