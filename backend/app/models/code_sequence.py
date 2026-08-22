from sqlalchemy import CheckConstraint, Column, Integer, String

from app.db.database import Base


class CodeSequence(Base):
    __tablename__ = "code_sequences"

    __table_args__ = (
        CheckConstraint(
            "last_value >= 0",
            name="ck_code_sequences_last_value_non_negative",
        ),
    )

    entity_key = Column(
        String(50),
        primary_key=True,
    )
    last_value = Column(
        Integer,
        nullable=False,
        default=0,
    )