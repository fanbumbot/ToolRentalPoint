from sqlalchemy import and_

from .base.crud_base_dto import *

from .....domain.item_distribution.item_status import ItemStatus

from .....infrastructure.models import CategoryModel

def convert_name(key: str, name: str, session: Session):
    if len(name) < 1 or len(name) > 64:
        raise FieldValidationError("Название товара должно быть от 1 до 64 символов", key)
    return name

@dataclass(frozen=True)
class CategoryCreateDTO(CreateDTO):
    @classmethod
    def get_model_by_data(cls, session: Session, data: dict[str, object]):
        args = cls._get_values_for_model_by_data(session, data)
        model = CategoryModel(**args)
        return model
    
    @classmethod
    def create_by_data(cls, session, data):
        model = cls.get_model_by_data(session, data)

        discount = session.query(CategoryModel).filter(
            CategoryModel.name == model.name
        ).one_or_none()

        if discount != None:
            raise FieldValidationError("Категория товара с таким именем уже существует")

        session.add(model)
        session.flush([model])

        return model

    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("name", "Название категории товара", convert_name)
        ])

    @classmethod
    def get(cls):
        return CategoryCreateDTO()

@dataclass(frozen=True)
class CategoryEditDTO(EditDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("name", "Название категории товара", convert_name)
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(CategoryModel).filter(
            CategoryModel.id == id
        ).one_or_none()

        if model == None:
            return None
        
        dto = CategoryEditDTO(id, values={
            "name": model.name
        })

        return dto

    @classmethod
    def update(cls, id, session: Session, data):
        dto = cls.get(id, session, data)

        model = session.query(CategoryModel).filter(
            CategoryModel.id == id
        ).one_or_none()

        if model == None:
            raise FieldValidationError("Категория товара для изменения не найдена")
        
        other_models_count = session.query(CategoryModel).filter(
            and_(
                CategoryModel.id != id,
                CategoryModel.name == data["name"]
            )
        ).count()

        if other_models_count != 0:
            raise FieldValidationError("Категория товара с таким именем уже существует")
        
        for key, value in dto.values.items():
            setattr(model, key, value)

@dataclass(frozen=True)
class CategoryShortViewDTO(ShortViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("name", "Название")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(CategoryModel).filter(
            CategoryModel.id == id
        ).one_or_none()

        if model == None:
            return

        dto = CategoryShortViewDTO(id, values={
            "id": id,
            "name": model.name
        })

        return dto

@dataclass(frozen=True)
class CategoryLongViewDTO(LongViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("name", "Название")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(CategoryModel).filter(
            CategoryModel.id == id
        ).one_or_none()

        if model == None:
            return

        dto = CategoryShortViewDTO(id, values={
            "id": id,
            "name": model.name
        })

        return dto