from sqlalchemy.orm import Session, Query
from typing import Type

from .service.dto.crud.base.crud_base_dto import CreateDTO, EditDTO, LongViewDTO, ShortViewDTO

class BaseCRUDService:
    def __init__(
        self,
        session: Session,
        model_type: type,

        create_dto_type: Type[CreateDTO],
        edit_dto_type: Type[EditDTO],
        long_view_dto_type: Type[LongViewDTO],
        short_view_dto_type: Type[ShortViewDTO]
    ):
        self.session = session
        self.model_type = model_type

        self.create_dto_type = create_dto_type
        self.edit_dto_type = edit_dto_type
        self.long_view_dto_type = long_view_dto_type
        self.short_view_dto_type = short_view_dto_type

    def get_all(self, page: int, page_size: int):
        query = self.session.query(self.model_type.id)
        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()
        
        dtos = list()
        for row in rows:
            id = row.tuple()[0]
            dto = self.short_view_dto_type.get_by_id(self.session, id)
            dtos.append(dto)
        return dtos, total

    def get_detail(self, id):
        dto = self.long_view_dto_type.get_by_id(self.session, id)
        return dto

    def get_model_by_id(self, id):
        model = self.session.query(self.model_type).filter(
            self.model_type.id == id
        ).one_or_none()

        return model
    
    def get_create_dto(self):
        dto = self.create_dto_type.get()
        return dto
    
    def get_edit_dto(self, id):
        dto = self.edit_dto_type.get_by_id(self.session, id)
        return dto
    
    def create(self, data: dict):
        dto = self.create_dto_type.create_by_data(self.session, data)
        return dto
    
    def update(self, id: int, data: dict):
        self.edit_dto_type.update(id, self.session, data)
    
    def delete(self, id):
        model = self.get_model_by_id(id)
        self.session.delete(model)