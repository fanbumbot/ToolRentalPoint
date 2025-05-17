from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .....domain.discount.implementation.queries.is_discount_season_belonged import IsDiscountSeasonBelongedQuery
from .....domain.discount.discount_season import DiscountSeason
from .....domain.discount.period import Period

from .....infrastructure.models import DiscountPeriodModel

class IsDiscountSeasonBelongedQueryImpl(IsDiscountSeasonBelongedQuery):
    def __init__(self, session: Session):
        self.session = session

    def __call__(self, period: Period) -> bool:
        count = self.session.query(DiscountPeriodModel).filter(
            or_(
                and_(
                    period.start_datetime >= DiscountPeriodModel.start,
                    period.start_datetime <= DiscountPeriodModel.end
                ),
                and_(
                    period.end_datetime >= DiscountPeriodModel.start,
                    period.end_datetime <= DiscountPeriodModel.end
                )
            )
        ).count()

        return count > 0