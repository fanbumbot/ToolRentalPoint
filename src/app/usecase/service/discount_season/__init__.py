from sqlalchemy.orm import Session
from sqlalchemy import and_

from ....domain.entity import EntityCQImpl

from ....infrastructure.models import DiscountPeriodModel

from ...base_crud_service import BaseCRUDService

from ..dto.crud.discount_season import DiscountSeasonCreateDTO, DiscountSeasonEditDTO, DiscountSeasonLongViewDTO, DiscountSeasonShortViewDTO

class DiscountSeasonService(BaseCRUDService):
    def __init__(
        self,
        session: Session
    ):
        super().__init__(session, DiscountPeriodModel,
            DiscountSeasonCreateDTO, DiscountSeasonEditDTO, DiscountSeasonLongViewDTO, DiscountSeasonShortViewDTO)