from sqlalchemy import and_

from .base.crud_base_dto import *

from .....domain.item_distribution.item_status import ItemStatus

from .....infrastructure.models import ProductModel, ItemModel, CategoryModel, UserModel, OrderModel

def convert_product_id(key: str, product_id_str, session: Session):
    try:
        product_id = int(product_id_str)
    except:
        raise FieldValidationError("Введённое значение не является целым числом", key)

    model = session.query(ProductModel).filter(
        ProductModel.id == product_id
    ).one_or_none()
    if model == None:
        raise FieldValidationError("Товара с таким ID не существует", key)

    return product_id

def status_to_str(status: str):
    match status:
        case ItemStatus.OnStock.name:
            return "На складе"
        case ItemStatus.Allocated.name:
            return "Выделено для заказа"
        case ItemStatus.Rented.name:
            return "Арендовано"
        case ItemStatus.Sold.name:
            return "Куплено"
        case _:
            return "Неизвестно"
        

@dataclass(frozen=True)
class ItemCreateDTO(CreateDTO):
    @classmethod
    def get_model_by_data(cls, session: Session, data: dict[str, object]):
        args = cls._get_values_for_model_by_data(session, data)
        args["status"] = ItemStatus.OnStock.name
        args["is_in_stock"] = False
        args["is_ready"] = False
        args["order_id"] = None
        model = ItemModel(**args)
        return model

    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("sticked_id", "SID"),
            FieldInput("product_id", "ID товара", convert_product_id)
        ])

    @classmethod
    def get(cls):
        return ItemCreateDTO()
    
    @classmethod
    def create_by_data(cls, session, data):
        model = cls.get_model_by_data(session, data)

        check_model = session.query(ItemModel).filter(
            ItemModel.sticked_id == model.sticked_id
        ).one_or_none()

        if check_model != None:
            raise FieldValidationError("Товар на складе с таким SID уже существует")

        session.add(model)
        session.flush([model])

        return model

@dataclass(frozen=True)
class ItemEditDTO(EditDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("sticked_id", "SID"),
            FieldInput("product_id", "ID товара", convert_product_id),
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(ItemModel).filter(
            ItemModel.id == id
        ).one_or_none()

        if model == None:
            return None
        
        dto = ItemEditDTO(id, values={
            "sticked_id": model.sticked_id,
            "product_id": model.product_id,
            "status": model.status
        })

        return dto
    
    @classmethod
    def update(cls, id, session: Session, data: dict[str, object]):
        dto = cls.get(id, session, data)

        model = session.query(ItemModel).filter(
            ItemModel.id == id
        ).one_or_none()

        if model == None:
            raise FieldValidationError("Товар на складе для изменения не найден")
        
        check_model = session.query(ItemModel).filter(
            and_(
                ItemModel.sticked_id == data["sticked_id"],
                ItemModel.id != id
            )
        )

        if check_model != None:
            raise FieldValidationError("Товар на складе с таким SID уже существует")
        
        for key, value in dto.values.items():
            setattr(model, key, value)

@dataclass(frozen=True)
class ItemShortViewDTO(ShortViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("sticked_id", "SID"),
            FieldView("status", "Статус")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(ItemModel).filter(
            ItemModel.id == id
        ).one_or_none()

        if model == None:
            return None
        
        dto = ItemShortViewDTO(id, values={
            "sticked_id": model.sticked_id,
            "status": status_to_str(model.status)
        })

        return dto

@dataclass(frozen=True)
class ItemLongViewDTO(LongViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("sticked_id", "SID"),
            FieldView("status", "Статус"),
            FieldView("product_name", "Название товара"),
            FieldView("category_name", "Название категории товара"),
            FieldView("owner_name", "Владелец")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        item_model = session.query(ItemModel).filter(
            ItemModel.id == id
        ).one_or_none()

        if item_model == None:
            return None
        
        product_model = session.query(ProductModel).filter(
            ProductModel.id == item_model.product_id
        ).one_or_none()

        if product_model == None:
            return None
        
        category_model = session.query(CategoryModel).filter(
            CategoryModel.id == product_model.category_id
        ).one_or_none()

        if category_model == None:
            return None
        
        order_model = session.query(OrderModel).filter(
            OrderModel.id == item_model.order_id
        ).one_or_none()

        if order_model == None:
            return None
        
        user_model = session.query(UserModel).filter(
            UserModel.id == order_model.user_id
        ).one_or_none()
        
        user_name = user_model.login if user_model else "-"

        dto = ItemLongViewDTO(id, values={
            "id": item_model.id,
            "sticked_id": item_model.sticked_id,
            "status": status_to_str(item_model.status),
            "product_name": product_model.name,
            "category_name": category_model.name,
            "owner_name": user_name
        })

        return dto