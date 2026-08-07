from sqlalchemy import Column, String, Text

from app.common.base_model import BaseModel


class Customer(BaseModel):
    __tablename__ = "customers"

    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    tax_id = Column(String(30), nullable=True, unique=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)