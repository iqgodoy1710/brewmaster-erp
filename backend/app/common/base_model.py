from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import declared_attr

from app.db.database import Base


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)

    @declared_attr
    def active(cls):
        return Column(Boolean, nullable=False, default=True)

    @declared_attr
    def created_at(cls):
        return Column(
            TIMESTAMP,
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls):
        return Column(
            TIMESTAMP,
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )