from app.models.beer_presentation import BeerPresentation
from app.schemas.beer_presentation import BeerPresentationCreate
from sqlalchemy.orm import Session


def get_beer_presentations(
    db: Session,
) -> list[BeerPresentation]:
    return db.query(BeerPresentation).filter(BeerPresentation.active.is_(True)).all()


def get_beer_presentation_by_code(
    db: Session,
    code: str,
) -> BeerPresentation | None:
    return db.query(BeerPresentation).filter(BeerPresentation.code == code).first()


def get_beer_presentation_by_name(
    db: Session,
    name: str,
) -> BeerPresentation | None:
    return db.query(BeerPresentation).filter(BeerPresentation.name == name).first()


def get_beer_presentation_by_beer_id_and_packaging_format_id(
    db: Session,
    beer_id: int,
    packaging_format_id: int,
) -> BeerPresentation | None:
    return (
        db.query(BeerPresentation)
        .filter(
            BeerPresentation.beer_id == beer_id,
            BeerPresentation.packaging_format_id == packaging_format_id,
        )
        .first()
    )


def create_beer_presentation(
    db: Session,
    presentation_data: BeerPresentationCreate,
    code: str,
) -> BeerPresentation:
    presentation = BeerPresentation(
        code=code,
        **presentation_data.model_dump(),
    )

    db.add(presentation)
    db.commit()
    db.refresh(presentation)

    return presentation


def get_beer_presentation_by_id(
    db: Session,
    beer_presentation_id: int,
) -> BeerPresentation | None:
    return (
        db.query(BeerPresentation)
        .filter(BeerPresentation.id == beer_presentation_id)
        .first()
    )


def update_beer_presentation_stock(
    db: Session,
    beer_presentation: BeerPresentation,
    current_stock: int,
) -> BeerPresentation:
    beer_presentation.current_stock = current_stock

    db.flush()

    return beer_presentation


def update_beer_presentation_minimum_stock(
    db: Session,
    beer_presentation: BeerPresentation,
    minimum_stock: int,
) -> BeerPresentation:
    beer_presentation.minimum_stock = minimum_stock

    db.commit()
    db.refresh(beer_presentation)

    return beer_presentation


def get_beer_presentations_at_or_below_minimum_stock(
    db: Session,
) -> list[BeerPresentation]:
    return (
        db.query(BeerPresentation)
        .filter(
            BeerPresentation.active.is_(True),
            BeerPresentation.minimum_stock > 0,
            BeerPresentation.current_stock <= BeerPresentation.minimum_stock,
        )
        .order_by(BeerPresentation.name)
        .all()
    )
