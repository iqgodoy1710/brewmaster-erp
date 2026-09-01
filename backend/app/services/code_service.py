from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.code_sequence import CodeSequence


_CODE_PREFIXES = {
    "sale": "VEN",
    "packaging_run": "ENV",
    "customer": "CLI",
    "raw_material": "INS",
    "beer": "CER",
    "packaging_format": "FOR",
    "beer_presentation": "PRE",
    "customer_payment": "PAG",
    "keg_repackaging_run" : "ENV2",
    "delivery_order": "PED",
    "delivery_note": "REM",
}


def generate_code(
    db: Session,
    entity_key: str,
) -> str:
    prefix = _CODE_PREFIXES[entity_key]

    statement = (
        insert(CodeSequence)
        .values(
            entity_key=entity_key,
            last_value=1,
        )
        .on_conflict_do_update(
            index_elements=[CodeSequence.entity_key],
            set_={
                "last_value": CodeSequence.last_value + 1,
            },
        )
        .returning(CodeSequence.last_value)
    )

    next_value = db.execute(statement).scalar_one()

    return f"{prefix}-{next_value:06d}"