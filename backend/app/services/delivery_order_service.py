from decimal import Decimal

from app.common.exceptions import (
    BeerPresentationNotFoundError,
    CustomerNotFoundError,
    DeliveryOrderHasNoItemsError,
    DeliveryOrderItemAlreadyExistsError,
    DeliveryOrderItemNotFoundError,
    DeliveryOrderKegAlreadyExistsError,
    DeliveryOrderNotFoundError,
    InactiveBeerPresentationError,
    InactiveCustomerError,
    InactiveKegError,
    InvalidDeliveryOrderCloseError,
    InvalidDeliveryOrderItemError,
    InvalidDeliveryOrderKegError,
    InvalidDeliveryOrderStatusError,
    KegNotFoundError,
)
from app.crud.beer_presentation import (
    get_beer_presentation_by_id,
    update_beer_presentation_stock,
)
from app.crud.beer_presentation_stock_movement import (
    create_delivery_movement,
)
from app.crud.customer import get_customer_by_id
from app.crud.customer_account_movement import (
    create_customer_account_movement,
)
from app.crud.delivery_order import (
    cancel_delivery_order,
    create_delivery_order,
    create_delivery_order_item,
    create_delivery_order_keg,
    delete_delivery_order_item,
    delete_delivery_order_keg,
    get_delivery_order_by_code,
    get_delivery_order_detail_by_code,
    get_delivery_order_item_by_id,
    get_delivery_order_item_by_order_and_beer_presentation,
    get_delivery_order_keg_by_order_and_keg,
    get_delivery_order_kegs,
    get_delivery_orders,
    get_open_delivery_order_keg_assignment_by_keg_id,
    mark_delivery_order_closed,
    mark_delivery_order_delivered,
    start_delivery_order_picking,
    update_delivery_order,
    update_delivery_order_item,
    update_delivery_order_item_picking,
)
from app.crud.keg import (
    get_keg_by_id,
    update_keg_state,
)
from app.crud.keg_movement import create_keg_movement
from app.crud.sale import complete_sale, create_sale
from app.crud.sale_item import create_sale_item
from app.models.enums import (
    CustomerAccountMovementType,
    DeliveryOrderStatus,
    KegMovementType,
    KegStatus,
    PackagingFormatType,
)
from app.schemas.delivery_order import (
    DeliveryOrderClose,
    DeliveryOrderCreate,
    DeliveryOrderDeliver,
    DeliveryOrderItemCreate,
    DeliveryOrderItemUpdate,
    DeliveryOrderKegCreate,
    DeliveryOrderPickingUpdate,
    DeliveryOrderUpdate,
)
from app.schemas.sale import SaleCreate
from app.schemas.sale_item import SaleItemCreate
from app.services.code_service import generate_code
from sqlalchemy.orm import Session


class DeliveryOrderService:
    @staticmethod
    def get_all(
        db: Session,
    ):
        return get_delivery_orders(db)

    @staticmethod
    def get_detail(
        db: Session,
        code: str,
    ):
        delivery_order = get_delivery_order_detail_by_code(db, code)

        if not delivery_order:
            raise DeliveryOrderNotFoundError("The delivery order does not exist.")

        return delivery_order

    @staticmethod
    def create(
        db: Session,
        delivery_order_data: DeliveryOrderCreate,
    ):
        customer = get_customer_by_id(
            db,
            delivery_order_data.customer_id,
        )
        if not customer:
            raise CustomerNotFoundError("The customer does not exist.")

        if not customer.active:
            raise InactiveCustomerError(
                "Cannot create a delivery order for an inactive customer."
            )

        try:
            delivery_order = create_delivery_order(
                db,
                delivery_order_data,
                generate_code(db, "delivery_order"),
            )
            db.commit()
            db.refresh(delivery_order)
        except Exception:
            db.rollback()
            raise

        return delivery_order

    @staticmethod
    def update(
        db: Session,
        code: str,
        delivery_order_data: DeliveryOrderUpdate,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.DRAFT,
            "Only draft delivery orders can be updated.",
        )

        if delivery_order_data.customer_id is not None:
            customer = get_customer_by_id(
                db,
                delivery_order_data.customer_id,
            )
            if not customer:
                raise CustomerNotFoundError("The customer does not exist.")

            if not customer.active:
                raise InactiveCustomerError(
                    "Cannot assign an inactive customer to a delivery order."
                )

        try:
            update_delivery_order(
                db,
                delivery_order,
                delivery_order_data,
            )
            db.commit()
            db.refresh(delivery_order)
        except Exception:
            db.rollback()
            raise

        return delivery_order

    @staticmethod
    def add_item(
        db: Session,
        code: str,
        item_data: DeliveryOrderItemCreate,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.DRAFT,
            "Items can only be added to draft delivery orders.",
        )

        beer_presentation = get_beer_presentation_by_id(
            db,
            item_data.beer_presentation_id,
        )
        if not beer_presentation:
            raise BeerPresentationNotFoundError("The beer presentation does not exist.")

        if not beer_presentation.active:
            raise InactiveBeerPresentationError(
                "Cannot add an inactive beer presentation to a delivery order."
            )

        existing_item = get_delivery_order_item_by_order_and_beer_presentation(
            db,
            delivery_order.id,
            item_data.beer_presentation_id,
        )
        if existing_item:
            raise DeliveryOrderItemAlreadyExistsError(
                "This beer presentation is already included in the delivery order."
            )

        try:
            item = create_delivery_order_item(
                db,
                delivery_order.id,
                item_data,
            )
            db.commit()
            db.refresh(item)
        except Exception:
            db.rollback()
            raise

        return item

    @staticmethod
    def update_item(
        db: Session,
        code: str,
        delivery_order_item_id: int,
        item_data: DeliveryOrderItemUpdate,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.DRAFT,
            "Items can only be updated in draft delivery orders.",
        )

        item = DeliveryOrderService._get_order_item(
            db,
            delivery_order.id,
            delivery_order_item_id,
        )

        try:
            update_delivery_order_item(
                db,
                item,
                item_data,
            )
            db.commit()
            db.refresh(item)
        except Exception:
            db.rollback()
            raise

        return item

    @staticmethod
    def remove_item(
        db: Session,
        code: str,
        delivery_order_item_id: int,
    ) -> None:
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.DRAFT,
            "Items can only be removed from draft delivery orders.",
        )

        item = DeliveryOrderService._get_order_item(
            db,
            delivery_order.id,
            delivery_order_item_id,
        )

        try:
            delete_delivery_order_item(db, item)
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def start_picking(
        db: Session,
        code: str,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.DRAFT,
            "Only draft delivery orders can start picking.",
        )

        if not delivery_order.items:
            raise DeliveryOrderHasNoItemsError(
                "Cannot start picking a delivery order without items."
            )

        try:
            start_delivery_order_picking(db, delivery_order)
            db.commit()
            db.refresh(delivery_order)
        except Exception:
            db.rollback()
            raise

        return delivery_order

    @staticmethod
    def update_picking(
        db: Session,
        code: str,
        delivery_order_item_id: int,
        picking_data: DeliveryOrderPickingUpdate,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.PICKING,
            "Picking quantities can only be updated while picking.",
        )

        item = DeliveryOrderService._get_order_item(
            db,
            delivery_order.id,
            delivery_order_item_id,
        )

        if picking_data.picked_quantity > item.requested_quantity:
            raise InvalidDeliveryOrderItemError(
                "Picked quantity cannot exceed requested quantity."
            )

        beer_presentation = get_beer_presentation_by_id(
            db,
            item.beer_presentation_id,
        )
        if not beer_presentation or not beer_presentation.active:
            raise InvalidDeliveryOrderItemError(
                "The beer presentation is not available for picking."
            )

        if picking_data.picked_quantity > beer_presentation.current_stock:
            raise InvalidDeliveryOrderItemError(
                "There is not enough finished product stock for this picking quantity."
            )

        try:
            item = update_delivery_order_item_picking(
                db,
                item,
                picking_data.picked_quantity,
            )
            db.commit()
            db.refresh(item)
        except Exception:
            db.rollback()
            raise

        return item

    @staticmethod
    def assign_keg(
        db: Session,
        code: str,
        keg_data: DeliveryOrderKegCreate,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.PICKING,
            "Kegs can only be assigned while picking.",
        )

        keg = get_keg_by_id(db, keg_data.keg_id)
        if not keg:
            raise KegNotFoundError("The keg does not exist.")

        if not keg.active:
            raise InactiveKegError("Cannot assign an inactive keg to a delivery order.")

        if keg.status != KegStatus.FILLED or keg.beer_presentation_id is None:
            raise InvalidDeliveryOrderKegError(
                "Only filled kegs can be assigned to a delivery order."
            )

        item = get_delivery_order_item_by_order_and_beer_presentation(
            db,
            delivery_order.id,
            keg.beer_presentation_id,
        )
        if not item or item.picked_quantity == 0:
            raise InvalidDeliveryOrderKegError(
                "Pick units of this keg presentation before assigning physical kegs."
            )

        existing_assignment = get_delivery_order_keg_by_order_and_keg(
            db,
            delivery_order.id,
            keg.id,
        )
        if existing_assignment:
            raise DeliveryOrderKegAlreadyExistsError(
                "This keg is already assigned to the delivery order."
            )
        open_assignment = get_open_delivery_order_keg_assignment_by_keg_id(
            db,
            keg.id,
        )
        if open_assignment:
            raise InvalidDeliveryOrderKegError(
                "This keg is already assigned to another open delivery order."
            )

        assigned_kegs = get_delivery_order_kegs(
            db,
            delivery_order.id,
        )
        assigned_quantity = sum(
            1
            for assigned_keg in assigned_kegs
            if assigned_keg.keg.beer_presentation_id == keg.beer_presentation_id
        )
        if assigned_quantity >= item.picked_quantity:
            raise InvalidDeliveryOrderKegError(
                "There cannot be more assigned kegs than picked units."
            )

        try:
            assignment = create_delivery_order_keg(
                db,
                delivery_order.id,
                keg.id,
            )
            db.commit()
            db.refresh(assignment)
        except Exception:
            db.rollback()
            raise

        return assignment

    @staticmethod
    def remove_keg(
        db: Session,
        code: str,
        keg_id: int,
    ) -> None:
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.PICKING,
            "Kegs can only be removed while picking.",
        )

        assignment = get_delivery_order_keg_by_order_and_keg(
            db,
            delivery_order.id,
            keg_id,
        )
        if not assignment:
            raise InvalidDeliveryOrderKegError(
                "The keg is not assigned to this delivery order."
            )

        try:
            delete_delivery_order_keg(db, assignment)
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def deliver(
        db: Session,
        code: str,
        delivery_data: DeliveryOrderDeliver,
        performed_by_user_id: int | None,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.PICKING,
            "Only delivery orders in picking can be delivered.",
        )

        items_with_quantity = [
            item for item in delivery_order.items if item.picked_quantity > 0
        ]
        if not items_with_quantity:
            raise InvalidDeliveryOrderItemError(
                "Pick at least one item before delivering the order."
            )

        presentations_by_id = {}

        for item in items_with_quantity:
            beer_presentation = get_beer_presentation_by_id(
                db,
                item.beer_presentation_id,
            )
            if not beer_presentation or not beer_presentation.active:
                raise InvalidDeliveryOrderItemError(
                    "A picked beer presentation is not available."
                )

            if beer_presentation.current_stock < item.picked_quantity:
                raise InvalidDeliveryOrderItemError(
                    "There is not enough finished product stock to deliver the order."
                )

            presentations_by_id[beer_presentation.id] = beer_presentation

        assignments = get_delivery_order_kegs(
            db,
            delivery_order.id,
        )
        assigned_kegs_by_presentation: dict[int, list] = {}

        for assignment in assignments:
            keg = get_keg_by_id(db, assignment.keg_id)

            if (
                not keg
                or not keg.active
                or keg.status != KegStatus.FILLED
                or keg.beer_presentation_id is None
            ):
                raise InvalidDeliveryOrderKegError(
                    "An assigned keg is no longer available for delivery."
                )

            if keg.beer_presentation_id not in presentations_by_id:
                raise InvalidDeliveryOrderKegError(
                    "An assigned keg does not match a picked order item."
                )

            assigned_kegs_by_presentation.setdefault(
                keg.beer_presentation_id,
                [],
            ).append(keg)

        for item in items_with_quantity:
            beer_presentation = presentations_by_id[item.beer_presentation_id]

            if (
                beer_presentation.packaging_format.format_type
                == PackagingFormatType.KEG
            ):
                assigned_kegs = assigned_kegs_by_presentation.get(
                    beer_presentation.id,
                    [],
                )
                if len(assigned_kegs) != item.picked_quantity:
                    raise InvalidDeliveryOrderKegError(
                        "Each picked keg unit must have one assigned physical keg."
                    )

        delivery_note_code = generate_code(db, "delivery_note")

        try:
            for item in items_with_quantity:
                beer_presentation = presentations_by_id[item.beer_presentation_id]

                item.delivered_quantity = item.picked_quantity

                create_delivery_movement(
                    db,
                    beer_presentation_id=beer_presentation.id,
                    delivery_order_id=delivery_order.id,
                    quantity=item.delivered_quantity,
                    reference=delivery_note_code,
                    notes=(
                        f"Finished product delivery for order {delivery_order.code}."
                    ),
                )
                update_beer_presentation_stock(
                    db,
                    beer_presentation,
                    beer_presentation.current_stock - item.delivered_quantity,
                )

            for assigned_kegs in assigned_kegs_by_presentation.values():
                for keg in assigned_kegs:
                    create_keg_movement(
                        db,
                        keg_id=keg.id,
                        movement_type=KegMovementType.DELIVERY,
                        previous_status=keg.status,
                        new_status=KegStatus.AT_CUSTOMER,
                        resulting_volume_liters=keg.current_volume_liters,
                        beer_presentation_id=keg.beer_presentation_id,
                        production_batch_id=keg.production_batch_id,
                        customer_id=delivery_order.customer_id,
                        delivery_order_id=delivery_order.id,
                        reference=delivery_note_code,
                        notes=(
                            delivery_data.notes
                            or f"Keg delivery for order {delivery_order.code}."
                        ),
                        performed_by_user_id=performed_by_user_id,
                    )
                    update_keg_state(
                        db,
                        keg,
                        status=KegStatus.AT_CUSTOMER,
                        current_volume_liters=keg.current_volume_liters,
                        beer_presentation_id=keg.beer_presentation_id,
                        production_batch_id=keg.production_batch_id,
                        customer_id=delivery_order.customer_id,
                    )

            mark_delivery_order_delivered(
                db,
                delivery_order,
                delivery_note_code=delivery_note_code,
                delivered_by_user_id=performed_by_user_id,
                notes=delivery_data.notes,
            )
            db.commit()
            db.refresh(delivery_order)
        except Exception:
            db.rollback()
            raise

        return delivery_order

    @staticmethod
    def close(
        db: Session,
        code: str,
        close_data: DeliveryOrderClose,
        closed_by_user_id: int | None,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        DeliveryOrderService._require_status(
            delivery_order,
            DeliveryOrderStatus.DELIVERED_PENDING_PRICING,
            "Only delivered orders pending pricing can be closed.",
        )

        delivered_items = [
            item for item in delivery_order.items if item.delivered_quantity > 0
        ]
        if not delivered_items:
            raise InvalidDeliveryOrderCloseError(
                "Cannot close a delivery order without delivered items."
            )

        delivered_item_ids = {item.id for item in delivered_items}
        prices_by_item_id: dict[int, Decimal] = {}

        for price_review in close_data.items:
            if price_review.delivery_order_item_id not in delivered_item_ids:
                raise InvalidDeliveryOrderCloseError(
                    "Prices can only be reviewed for delivered order items."
                )

            if price_review.delivery_order_item_id in prices_by_item_id:
                raise InvalidDeliveryOrderCloseError(
                    "Each delivered order item must have one reviewed price."
                )

            prices_by_item_id[price_review.delivery_order_item_id] = (
                price_review.unit_price
            )

        if set(prices_by_item_id) != delivered_item_ids:
            raise InvalidDeliveryOrderCloseError(
                "A reviewed price is required for every delivered order item."
            )

        try:
            sale = create_sale(
                db,
                SaleCreate(
                    customer_id=delivery_order.customer_id,
                    notes=(
                        close_data.notes
                        or (
                            f"Generated from delivery order "
                            f"{delivery_order.code} "
                            f"and delivery note "
                            f"{delivery_order.delivery_note_code}."
                        )
                    ),
                ),
                code=generate_code(db, "sale"),
                delivery_order_id=delivery_order.id,
                commit=False,
            )

            total_amount = Decimal("0.00")

            for item in delivered_items:
                unit_price = prices_by_item_id[item.id]

                create_sale_item(
                    db,
                    SaleItemCreate(
                        sale_id=sale.id,
                        beer_presentation_id=item.beer_presentation_id,
                        quantity=item.delivered_quantity,
                    ),
                    unit_price=unit_price,
                    commit=False,
                )

                total_amount += Decimal(item.delivered_quantity) * unit_price

            complete_sale(db, sale)

            create_customer_account_movement(
                db,
                customer_id=delivery_order.customer_id,
                sale_id=sale.id,
                movement_type=CustomerAccountMovementType.SALE_CHARGE,
                amount=total_amount,
                reference=sale.code,
                notes=(
                    f"Account charge generated from delivery note "
                    f"{delivery_order.delivery_note_code}."
                ),
            )

            mark_delivery_order_closed(
                db,
                delivery_order,
                closed_by_user_id=closed_by_user_id,
                notes=close_data.notes,
            )
            db.commit()
            db.refresh(sale)
        except Exception:
            db.rollback()
            raise

        return sale

    @staticmethod
    def cancel(
        db: Session,
        code: str,
    ):
        delivery_order = DeliveryOrderService.get_detail(db, code)

        if delivery_order.status not in {
            DeliveryOrderStatus.DRAFT,
            DeliveryOrderStatus.PICKING,
        }:
            raise InvalidDeliveryOrderStatusError(
                "Only draft or picking delivery orders can be cancelled."
            )

        try:
            cancel_delivery_order(db, delivery_order)
            db.commit()
            db.refresh(delivery_order)
        except Exception:
            db.rollback()
            raise

        return delivery_order

    @staticmethod
    def _get_order_item(
        db: Session,
        delivery_order_id: int,
        delivery_order_item_id: int,
    ):
        item = get_delivery_order_item_by_id(
            db,
            delivery_order_item_id,
        )

        if not item or item.delivery_order_id != delivery_order_id:
            raise DeliveryOrderItemNotFoundError(
                "The delivery order item does not exist."
            )

        return item

    @staticmethod
    def _require_status(
        delivery_order,
        required_status: DeliveryOrderStatus,
        message: str,
    ) -> None:
        if delivery_order.status != required_status:
            raise InvalidDeliveryOrderStatusError(message)
