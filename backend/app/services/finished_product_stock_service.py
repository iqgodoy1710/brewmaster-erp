from app.crud.beer_presentation import (
    get_packaged_finished_product_stock_summary,
)
from app.crud.keg import get_filled_keg_stock_summary
from app.schemas.finished_product_stock import (
    KegFinishedProductStockResponse,
    PackagedFinishedProductStockResponse,
)
from sqlalchemy.orm import Session


class FinishedProductStockService:
    @staticmethod
    def get_kegs(
        db: Session,
    ) -> list[KegFinishedProductStockResponse]:
        rows = get_filled_keg_stock_summary(db)

        return [
            KegFinishedProductStockResponse(
                beer_id=row.beer_id,
                beer_name=row.beer_name,
                beer_style=row.beer_style,
                packaging_format_id=row.packaging_format_id,
                packaging_format_name=row.packaging_format_name,
                form_factor=row.form_factor,
                keg_count=row.keg_count,
                total_volume_liters=row.total_volume_liters,
            )
            for row in rows
        ]

    @staticmethod
    def get_packaged(
        db: Session,
    ) -> list[PackagedFinishedProductStockResponse]:
        rows = get_packaged_finished_product_stock_summary(db)

        return [
            PackagedFinishedProductStockResponse(
                beer_presentation_id=row.beer_presentation_id,
                beer_presentation_code=row.beer_presentation_code,
                beer_presentation_name=row.beer_presentation_name,
                beer_name=row.beer_name,
                beer_style=row.beer_style,
                packaging_format_name=row.packaging_format_name,
                current_stock=row.current_stock,
                total_volume_liters=row.total_volume_liters,
            )
            for row in rows
        ]