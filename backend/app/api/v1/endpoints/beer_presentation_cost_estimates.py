from app.api.auth_dependencies import require_roles
from app.db.dependencies import get_db
from app.models.enums import UserRole
from app.schemas.beer_presentation_cost_estimate import (
    BeerPresentationCostEstimateResponse,
)
from app.services.beer_presentation_cost_estimate_service import (
    BeerPresentationCostEstimateService,
)
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Beer Presentation Cost Estimates"],
)


@router.get(
    "/beer-presentations/{beer_presentation_id}/cost-estimate",
    response_model=BeerPresentationCostEstimateResponse,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMIN,
                UserRole.MANAGEMENT,
            )
        )
    ],
)
def read_beer_presentation_cost_estimate(
    beer_presentation_id: int = Path(..., gt=0),
    recipe_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    return BeerPresentationCostEstimateService.get_estimate(
        db,
        beer_presentation_id,
        recipe_id,
    )