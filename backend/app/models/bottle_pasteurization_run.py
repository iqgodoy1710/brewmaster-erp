from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.common.base_model import BaseModel


class BottlePasteurizationRun(BaseModel):
    __tablename__ = "bottle_pasteurization_runs"

    __table_args__ = (
        CheckConstraint(
            "processed_quantity > 0",
            name=(
                "ck_bottle_pasteurization_runs_"
                "processed_quantity_positive"
            ),
        ),
        CheckConstraint(
            "approved_quantity >= 0",
            name=(
                "ck_bottle_pasteurization_runs_"
                "approved_quantity_non_negative"
            ),
        ),
        CheckConstraint(
            "waste_quantity >= 0",
            name=(
                "ck_bottle_pasteurization_runs_"
                "waste_quantity_non_negative"
            ),
        ),
        CheckConstraint(
            "processed_quantity = approved_quantity + waste_quantity",
            name=(
                "ck_bottle_pasteurization_runs_"
                "quantity_balance"
            ),
        ),
    )

    code = Column(
        String(30),
        nullable=False,
        unique=True,
    )

    beer_presentation_id = Column(
        Integer,
        ForeignKey("beer_presentations.id"),
        nullable=False,
    )

    processed_quantity = Column(
        Integer,
        nullable=False,
    )

    approved_quantity = Column(
        Integer,
        nullable=False,
    )

    waste_quantity = Column(
        Integer,
        nullable=False,
    )

    performed_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    occurred_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now(),
    )

    notes = Column(
        Text,
        nullable=True,
    )

    beer_presentation = relationship(
        "BeerPresentation",
        back_populates="pasteurization_runs",
    )

    performed_by_user = relationship("User")

    stock_movements = relationship(
        "BeerPresentationStockMovement",
        back_populates="pasteurization_run",
    )