from datetime import datetime

from app.models.delivery_order import (
    DeliveryOrder,
    DeliveryOrderItem,
    DeliveryOrderKeg,
)
from app.models.enums import DeliveryOrderStatus
from app.schemas.delivery_order import (
    DeliveryOrderCreate,
    DeliveryOrderItemCreate,
    DeliveryOrderItemUpdate,
    DeliveryOrderUpdate,
)
from sqlalchemy.orm import Session, selectinload


def get_delivery_orders(
    db: Session,
) -> list[DeliveryOrder]:
    return (
        db.query(DeliveryOrder)
        .filter(DeliveryOrder.active.is_(True))
        .order_by(DeliveryOrder.created_at.desc())
        .all()
    )


def get_delivery_order_by_code(
    db: Session,
    code: str,
) -> DeliveryOrder | None:
    return (
        db.query(DeliveryOrder)
        .filter(DeliveryOrder.code == code)
        .first()
    )


def get_delivery_order_detail_by_code(
    db: Session,
    code: str,
) -> DeliveryOrder | None:
    return (
        db.query(DeliveryOrder)
        .options(
            selectinload(DeliveryOrder.items),
            selectinload(DeliveryOrder.kegs),
        )
        .filter(DeliveryOrder.code == code)
        .first()
    )


def create_delivery_order(
    db: Session,
    delivery_order_data: DeliveryOrderCreate,
    code: str,
) -> DeliveryOrder:
    delivery_order = DeliveryOrder(
        code=code,
        customer_id=delivery_order_data.customer_id,
        notes=delivery_order_data.notes,
    )

    db.add(delivery_order)
    db.flush()

    return delivery_order


def update_delivery_order(
    db: Session,
    delivery_order: DeliveryOrder,
    delivery_order_data: DeliveryOrderUpdate,
) -> DeliveryOrder:
    for field, value in delivery_order_data.model_dump(
        exclude_unset=True,
    ).items():
        setattr(delivery_order, field, value)

    db.flush()

    return delivery_order


def create_delivery_order_item(
    db: Session,
    delivery_order_id: int,
    item_data: DeliveryOrderItemCreate,
) -> DeliveryOrderItem:
    item = DeliveryOrderItem(
        delivery_order_id=delivery_order_id,
        beer_presentation_id=item_data.beer_presentation_id,
        requested_quantity=item_data.requested_quantity,
        notes=item_data.notes,
    )

    db.add(item)
    db.flush()

    return item


def get_delivery_order_item_by_id(
    db: Session,
    delivery_order_item_id: int,
) -> DeliveryOrderItem | None:
    return (
        db.query(DeliveryOrderItem)
        .filter(DeliveryOrderItem.id == delivery_order_item_id)
        .first()
    )


def update_delivery_order_item(
    db: Session,
    item: DeliveryOrderItem,
    item_data: DeliveryOrderItemUpdate,
) -> DeliveryOrderItem:
    for field, value in item_data.model_dump(
        exclude_unset=True,
    ).items():
        setattr(item, field, value)

    db.flush()

    return item


def update_delivery_order_item_picking(
    db: Session,
    item: DeliveryOrderItem,
    picked_quantity: int,
) -> DeliveryOrderItem:
    item.picked_quantity = picked_quantity

    db.flush()

    return item


def delete_delivery_order_item(
    db: Session,
    item: DeliveryOrderItem,
) -> None:
    db.delete(item)
    db.flush()


def get_delivery_order_keg_by_order_and_keg(
    db: Session,
    delivery_order_id: int,
    keg_id: int,
) -> DeliveryOrderKeg | None:
    return (
        db.query(DeliveryOrderKeg)
        .filter(
            DeliveryOrderKeg.delivery_order_id == delivery_order_id,
            DeliveryOrderKeg.keg_id == keg_id,
        )
        .first()
    )


def create_delivery_order_keg(
    db: Session,
    delivery_order_id: int,
    keg_id: int,
) -> DeliveryOrderKeg:
    delivery_order_keg = DeliveryOrderKeg(
        delivery_order_id=delivery_order_id,
        keg_id=keg_id,
    )

    db.add(delivery_order_keg)
    db.flush()

    return delivery_order_keg


def delete_delivery_order_keg(
    db: Session,
    delivery_order_keg: DeliveryOrderKeg,
) -> None:
    db.delete(delivery_order_keg)
    db.flush()


def start_delivery_order_picking(
    db: Session,
    delivery_order: DeliveryOrder,
) -> DeliveryOrder:
    delivery_order.status = DeliveryOrderStatus.PICKING

    db.flush()

    return delivery_order


def mark_delivery_order_delivered(
    db: Session,
    delivery_order: DeliveryOrder,
    delivery_note_code: str,
    delivered_by_user_id: int | None,
    notes: str | None,
) -> DeliveryOrder:
    delivery_order.status = DeliveryOrderStatus.DELIVERED_PENDING_PRICING
    delivery_order.delivery_note_code = delivery_note_code
    delivery_order.delivered_at = datetime.now()
    delivery_order.delivered_by_user_id = delivered_by_user_id

    if notes is not None:
        delivery_order.notes = notes

    db.flush()

    return delivery_order


def mark_delivery_order_closed(
    db: Session,
    delivery_order: DeliveryOrder,
    closed_by_user_id: int | None,
    notes: str | None,
) -> DeliveryOrder:
    delivery_order.status = DeliveryOrderStatus.CLOSED
    delivery_order.closed_at = datetime.now()
    delivery_order.closed_by_user_id = closed_by_user_id

    if notes is not None:
        delivery_order.notes = notes

    db.flush()

    return delivery_order


def cancel_delivery_order(
    db: Session,
    delivery_order: DeliveryOrder,
) -> DeliveryOrder:
    delivery_order.status = DeliveryOrderStatus.CANCELLED

    db.flush()

    return delivery_order

def get_delivery_order_item_by_order_and_beer_presentation(
    db: Session,
    delivery_order_id: int,
    beer_presentation_id: int,
) -> DeliveryOrderItem | None:
    return (
        db.query(DeliveryOrderItem)
        .filter(
            DeliveryOrderItem.delivery_order_id == delivery_order_id,
            DeliveryOrderItem.beer_presentation_id == beer_presentation_id,
        )
        .first()
    )

def get_delivery_order_kegs(
    db: Session,
    delivery_order_id: int,
) -> list[DeliveryOrderKeg]:
    return (
        db.query(DeliveryOrderKeg)
        .filter(
            DeliveryOrderKeg.delivery_order_id == delivery_order_id,
            DeliveryOrderKeg.active.is_(True),
        )
        .all()
    )

def get_open_delivery_order_keg_assignment_by_keg_id(
    db: Session,
    keg_id: int,
) -> DeliveryOrderKeg | None:
    return (
        db.query(DeliveryOrderKeg)
        .join(
            DeliveryOrder,
            DeliveryOrderKeg.delivery_order_id == DeliveryOrder.id,
        )
        .filter(
            DeliveryOrderKeg.keg_id == keg_id,
            DeliveryOrder.active.is_(True),
            DeliveryOrder.status.in_(
                [
                    DeliveryOrderStatus.DRAFT,
                    DeliveryOrderStatus.PICKING,
                ]
            ),
        )
        .first()
    )