from sqlalchemy import (
    TIMESTAMP,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel
from app.models.enums import SaleStatus


class Sale(BaseModel):
    __tablename__ = "sales"

    code = Column(String(30), nullable=False, unique=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
    )
    status = Column(
        Enum(
            SaleStatus,
            name="sale_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
        default=SaleStatus.DRAFT,
    )
    completed_at = Column(TIMESTAMP, nullable=True)
    cancelled_at = Column(
        TIMESTAMP,
        nullable=True,
    )
    cancellation_reason = Column(Text)
    notes = Column(Text)

    customer = relationship(
        "Customer",
        back_populates="sales",
    )
    items = relationship(
        "SaleItem",
        back_populates="sale",
    )
    beer_presentation_stock_movements = relationship(
        "BeerPresentationStockMovement",
        back_populates="sale",
    )
