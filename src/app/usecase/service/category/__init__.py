from sqlalchemy.orm import Session
from sqlalchemy import and_

from ....domain.entity import EntityCQImpl

from ....infrastructure.models import CategoryModel

from ...base_crud_service import BaseCRUDService

from ..dto.crud.category import CategoryCreateDTO, CategoryEditDTO, CategoryLongViewDTO, CategoryShortViewDTO

class CategoryService(BaseCRUDService):
    def __init__(
        self,
        session: Session
    ):
        super().__init__(session, CategoryModel,
            CategoryCreateDTO, CategoryEditDTO, CategoryLongViewDTO, CategoryShortViewDTO)