from sqlalchemy import (
    CheckConstraint,
    Column,
    Numeric,
    String,
    Text,
)

from app.common.base_model import BaseModel


class PackagingFormat(BaseModel):
    __tablename__ = "packaging_formats"

    __table_args__ = (
        CheckConstraint(
            "capacity_liters > 0",
            name="ck_packaging_formats_capacity_liters_positive",
        ),
    )

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    capacity_liters = Column(
        Numeric(10, 3),
        nullable=False,
    )
    description = Column(Text)