from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.delivery_order import (
    DeliveryOrderClose,
    DeliveryOrderCreate,
    DeliveryOrderDeliver,
    DeliveryOrderDetailResponse,
    DeliveryOrderItemCreate,
    DeliveryOrderItemResponse,
    DeliveryOrderItemUpdate,
    DeliveryOrderKegCreate,
    DeliveryOrderKegResponse,
    DeliveryOrderPickingUpdate,
    DeliveryOrderResponse,
    DeliveryOrderUpdate,
)
from app.schemas.sale import SaleResponse
from app.services.delivery_order_service import DeliveryOrderService
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/delivery-orders",
    tags=["Delivery Orders"],
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.OPERATOR,
                UserRole.MANAGEMENT,
            )
        )
    ],
)


@router.get(
    "/",
    response_model=list[DeliveryOrderResponse],
)
def read_delivery_orders(
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.get_all(db)


@router.get(
    "/{code}",
    response_model=DeliveryOrderDetailResponse,
)
def read_delivery_order(
    code: str,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.get_detail(db, code)


@router.post(
    "/",
    response_model=DeliveryOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_delivery_order(
    delivery_order: DeliveryOrderCreate,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.create(db, delivery_order)


@router.patch(
    "/{code}",
    response_model=DeliveryOrderResponse,
)
def update_delivery_order(
    code: str,
    delivery_order: DeliveryOrderUpdate,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.update(
        db,
        code,
        delivery_order,
    )


@router.post(
    "/{code}/items",
    response_model=DeliveryOrderItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_delivery_order_item(
    code: str,
    item: DeliveryOrderItemCreate,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.add_item(db, code, item)


@router.patch(
    "/{code}/items/{delivery_order_item_id}",
    response_model=DeliveryOrderItemResponse,
)
def update_delivery_order_item(
    code: str,
    item: DeliveryOrderItemUpdate,
    delivery_order_item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.update_item(
        db,
        code,
        delivery_order_item_id,
        item,
    )


@router.delete(
    "/{code}/items/{delivery_order_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_delivery_order_item(
    code: str,
    delivery_order_item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    DeliveryOrderService.remove_item(
        db,
        code,
        delivery_order_item_id,
    )


@router.post(
    "/{code}/start-picking",
    response_model=DeliveryOrderResponse,
)
def start_delivery_order_picking(
    code: str,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.start_picking(db, code)


@router.patch(
    "/{code}/items/{delivery_order_item_id}/picking",
    response_model=DeliveryOrderItemResponse,
)
def update_delivery_order_picking(
    code: str,
    picking_data: DeliveryOrderPickingUpdate,
    delivery_order_item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.update_picking(
        db,
        code,
        delivery_order_item_id,
        picking_data,
    )


@router.post(
    "/{code}/kegs",
    response_model=DeliveryOrderKegResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_delivery_order_keg(
    code: str,
    keg_data: DeliveryOrderKegCreate,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.assign_keg(
        db,
        code,
        keg_data,
    )


@router.delete(
    "/{code}/kegs/{keg_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_delivery_order_keg(
    code: str,
    keg_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    DeliveryOrderService.remove_keg(db, code, keg_id)


@router.post(
    "/{code}/deliver",
    response_model=DeliveryOrderResponse,
)
def deliver_delivery_order(
    code: str,
    delivery_data: DeliveryOrderDeliver,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.OPERATOR,
            UserRole.MANAGEMENT,
        )
    ),
):
    return DeliveryOrderService.deliver(
        db,
        code,
        delivery_data,
        performed_by_user_id=(current_user.id if current_user else None),
    )


@router.post(
    "/{code}/close",
    response_model=SaleResponse,
)
def close_delivery_order(
    code: str,
    close_data: DeliveryOrderClose,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGEMENT,
        )
    ),
):
    return DeliveryOrderService.close(
        db,
        code,
        close_data,
        closed_by_user_id=(current_user.id if current_user else None),
    )


@router.post(
    "/{code}/cancel",
    response_model=DeliveryOrderResponse,
)
def cancel_delivery_order(
    code: str,
    db: Session = Depends(get_db),
):
    return DeliveryOrderService.cancel(db, code)
