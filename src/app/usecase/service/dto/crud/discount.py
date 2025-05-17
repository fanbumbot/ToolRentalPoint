from .base.crud_base_dto import *

from .....domain.item_distribution.item_status import ItemStatus

from .....infrastructure.models import DiscountModel, DiscountPeriodModel, ProductModel

def convert_model_id(key: str, id_str: str, session: Session, model_type, message_error: str):
    try:
        id = int(id_str)
    except:
        raise FieldValidationError("Введённое значение не является целым числом", key)
    
    model = session.query(model_type).filter(
        model_type.id == id
    ).one_or_none()
    if model == None:
        raise FieldValidationError(message_error, key)
    return model.id

def convert_product_id(key: str, product_id_str: str, session: Session):
    return convert_model_id(
        key,
        product_id_str,
        session,
        ProductModel,
        "Товара с таким id не существует"
    )

def convert_discount_season_id(key: str, discount_season_id_str: str, session: Session):
    return convert_model_id(
        key,
        discount_season_id_str,
        session,
        DiscountPeriodModel,
        "Сезона скидок с таким id не существует"
    )

def convert_discount(key: str, value: str, session: Session):
    if len(value) == 0:
        raise FieldValidationError("Скидка должна быть обязательно указана", key)
    value = value.strip()
    if value[-1] == "%":
        try:
            discount_in_percent = int(value[:-1])
            discount = discount_in_percent / 100
        except:
            raise FieldValidationError("Невозможно преобразовать в проценты", key)
    else:
        try:
            discount = float(value)
        except:
            raise FieldValidationError("Невозможно преобразовать в скидку", key)
        
    if discount < 0.0 or discount > 1.0:
        raise FieldValidationError("Скидка может быть от 0% до 100%", key)
    return discount

@dataclass(frozen=True)
class DiscountCreateDTO(CreateDTO):
    @classmethod
    def get_model_by_data(cls, session: Session, data: dict[str, object]):
        args = cls._get_values_for_model_by_data(session, data)
        model = DiscountModel(**args)
        return model
    
    @classmethod
    def create_by_data(cls, session, data):
        model = cls.get_model_by_data(session, data)

        discount = session.query(DiscountModel).filter(
            DiscountModel.product_id == model.product_id
        ).one_or_none()

        if discount != None:
            raise FieldValidationError("На данный товар уже есть скидка")

        session.add(model)
        session.flush([model])

        return model

    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("product_id", "ID товара", convert_product_id),
            FieldInput("discount_period_id", "ID периода скидок", convert_discount_season_id),
            FieldInput("discount_value", "Скидка (0.5 или 50%)", convert_discount)
        ])

    @classmethod
    def get(cls):
        return DiscountCreateDTO()

@dataclass(frozen=True)
class DiscountEditDTO(EditDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("product_id", "ID товара", convert_product_id),
            FieldInput("discount_period_id", "ID периода скидок", convert_discount_season_id),
            FieldInput("discount_value", "Скидка (0.5 или 50%)", convert_discount)
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(DiscountModel).filter(
            DiscountModel.id == id
        ).one_or_none()

        if model == None:
            return None
        
        dto = DiscountEditDTO(id, values={
            "product_id": model.product_id,
            "discount_period_id": model.discount_period_id,
            "discount_value": model.discount_value
        })

        return dto

    @classmethod
    def update(cls, id, session: Session, data):
        dto = cls.get(id, session, data)

        model = session.query(DiscountModel).filter(
            DiscountModel.id == id
        ).one_or_none()

        if model == None:
            raise FieldValidationError("Скидка для изменения не найдена")

        product_id = dto.values["product_id"]
        if product_id != model.product_id: # Произошло изменение
            discount = session.query(DiscountModel).filter(
                DiscountModel.product_id == product_id
            ).one_or_none()
            if discount != None:
                raise FieldValidationError("На данный товар уже есть скидка")

        for key, value in dto.values.items():
            setattr(model, key, value)

@dataclass(frozen=True)
class DiscountShortViewDTO(ShortViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("product_id", "ID товара"),
            FieldView("discount_value", "Скидка")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(DiscountModel).filter(
            DiscountModel.id == id
        ).one_or_none()

        if model == None:
            return

        dto = DiscountShortViewDTO(id, values={
            "id": id,
            "product_id": model.product_id,
            "discount_value": model.discount_value
        })

        return dto

@dataclass(frozen=True)
class DiscountLongViewDTO(LongViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("product_id", "ID товара"),
            FieldView("start", "Начало сезона скидок"),
            FieldView("end", "Конец сезона скидок")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(DiscountModel).filter(
            DiscountModel.id == id
        ).one_or_none()

        if model == None:
            return
        
        discount_period_model = session.query(DiscountPeriodModel).filter(
            DiscountPeriodModel.id == model.discount_period_id
        ).one_or_none()

        if discount_period_model == None:
            return

        dto = DiscountShortViewDTO(id, values={
            "id": id,
            "product_id": model.product_id,
            "discount_value": model.discount_value,
            "start": discount_period_model.start.strftime("%Y-%m-%d"),
            "end": discount_period_model.end.strftime("%Y-%m-%d")
        })

        return dto