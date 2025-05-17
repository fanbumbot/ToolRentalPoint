from .period import Period

from ..entity import Entity, EntityCQImpl
from ..validation import type_validate

from .implementation.queries.is_discount_season_belonged import IsDiscountSeasonBelongedQuery

class DiscountSeasonAlreadyExistsInThisPeriod(Exception):
    pass

class DiscountSeason(Entity):
    def __init__(
        self,
        id,
        impl: EntityCQImpl,
        period: Period
    ):
        super().__init__(id, impl)
        self.period = period

    @classmethod
    def create(cls, id, impl: EntityCQImpl, period: Period):
        type_validate(period, "Period", Period)
        impl.validate_from_domain([
            IsDiscountSeasonBelongedQuery
        ])

        if impl.call(IsDiscountSeasonBelongedQuery, period):
            raise DiscountSeasonAlreadyExistsInThisPeriod
        
        discount_season = DiscountSeason(id, impl, period)

        return discount_season
