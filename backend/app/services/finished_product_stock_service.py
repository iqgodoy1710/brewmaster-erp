from decimal import Decimal

from app.crud.beer import get_beer_keg_stock_coverage
from app.crud.beer_presentation import (
    get_packaged_finished_product_stock_summary,
)
from app.crud.keg import get_filled_keg_stock_summary
from app.schemas.finished_product_stock import (
    BeerKegStockCoverageResponse,
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
                keg_codes=sorted(row.keg_codes),
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

    @staticmethod
    def get_keg_coverage(
        db: Session,
    ) -> list[BeerKegStockCoverageResponse]:
        rows = get_beer_keg_stock_coverage(db)

        results = []

        for row in rows:
            minimum = Decimal(row.minimum_stock_liters)
            available = Decimal(row.available_keg_volume_liters)
            packaged = Decimal(row.packaged_volume_liters)
            available_bulk = Decimal(row.available_bulk_volume_liters)
            in_production = Decimal(row.in_production_volume_liters)
            physical_stock = available + packaged + available_bulk

            coverage = physical_stock + in_production
            shortage = max(
                Decimal("0.000"),
                minimum - coverage,
            )

            results.append(
                BeerKegStockCoverageResponse(
                    beer_id=row.beer_id,
                    beer_name=row.beer_name,
                    minimum_stock_liters=minimum,
                    available_keg_volume_liters=available,
                    in_production_volume_liters=in_production,
                    coverage_volume_liters=coverage,
                    shortage_volume_liters=shortage,
                    has_shortage=(minimum > 0 and coverage < minimum),
                    packaged_volume_liters=packaged,
                    available_bulk_volume_liters=available_bulk,
                    physical_stock_volume_liters=physical_stock,
                )
            )

        return results
