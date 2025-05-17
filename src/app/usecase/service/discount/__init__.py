from sqlalchemy.orm import Session
from sqlalchemy import and_

from ....domain.entity import EntityCQImpl

from ....infrastructure.models import DiscountModel, DiscountPeriodModel

from ...base_crud_service import BaseCRUDService

from ..dto.crud.discount import DiscountCreateDTO, DiscountEditDTO, DiscountLongViewDTO, DiscountShortViewDTO

class DiscountService(BaseCRUDService):
    def __init__(
        self,
        session: Session
    ):
        super().__init__(session, DiscountModel,
            DiscountCreateDTO, DiscountEditDTO, DiscountLongViewDTO, DiscountShortViewDTO)