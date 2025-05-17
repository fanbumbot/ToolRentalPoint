from sqlalchemy import and_, or_
from datetime import date, datetime

from .base.crud_base_dto import *

from .....domain.item_distribution.item_status import ItemStatus

from .....infrastructure.models import DiscountPeriodModel

def convert_date(key: str, date_str, session: Session):
    try:
        timestamp = datetime.fromisoformat(date_str)
    except:
        raise FieldValidationError("Введённое значение не является датой", key)
    return timestamp

@dataclass(frozen=True)
class DiscountSeasonCreateDTO(CreateDTO):
    @classmethod
    def get_model_by_data(cls, session: Session, data: dict[str, object]):
        args = cls._get_values_for_model_by_data(session, data)
        model = DiscountPeriodModel(**args)
        return model

    @classmethod
    def get_fields(cls):
        return Fields([
            FieldDateInput("start", "Начало сезона скидок", convert_date),
            FieldDateInput("end", "Конец сезона скидок", convert_date)
        ])

    @classmethod
    def get(cls):
        return DiscountSeasonCreateDTO()
    
    @classmethod
    def create_by_data(cls, session, data):
        model = cls.get_model_by_data(session, data)

        if data["start"] > data["end"]:
            raise FieldValidationError("Начало сезона не может быть позже конца")

        check_model_count = session.query(DiscountPeriodModel).filter(
            or_(
                and_(
                    DiscountPeriodModel.start <= data["start"],
                    DiscountPeriodModel.end >= data["start"],
                ),
                and_(
                    DiscountPeriodModel.start <= data["end"],
                    DiscountPeriodModel.end >= data["end"],
                )
            )
        ).count()

        if check_model_count != 0:
            raise FieldValidationError("Такой сезон будет пересекаться с другим сезоном")

        session.add(model)
        session.flush([model])
        return model

@dataclass(frozen=True)
class DiscountSeasonEditDTO(EditDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldDateInput("start", "Начало сезона скидок", convert_date),
            FieldDateInput("end", "Конец сезона скидок", convert_date),
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(DiscountPeriodModel).filter(
            DiscountPeriodModel.id == id
        ).one_or_none()

        if model == None:
            raise FieldValidationError("Сезон скидок для изменения не найден")
        
        dto = DiscountSeasonEditDTO(id, values={
            "start": model.start.strftime("%Y-%m-%d"),
            "end": model.end.strftime("%Y-%m-%d")
        })

        return dto

    @classmethod
    def update(cls, id, session: Session, data: dict[str, object]):
        dto = cls.get(id, session, data)

        if data["start"] > data["end"]:
            raise FieldValidationError("Начало сезона не может быть позже конца")

        check_model_count = session.query(DiscountPeriodModel).filter(
            and_(
                DiscountPeriodModel.id != id,
                or_(
                    and_(
                        DiscountPeriodModel.start <= data["start"],
                        DiscountPeriodModel.end >= data["start"],
                    ),
                    and_(
                        DiscountPeriodModel.start <= data["end"],
                        DiscountPeriodModel.end >= data["end"],
                    )
                )
            )
        ).count()

        if check_model_count != 0:
            raise FieldValidationError("Такой сезон будет пересекаться с другим сезоном")

        model = session.query(DiscountPeriodModel).filter(
            DiscountPeriodModel.id == id
        ).one_or_none()
        
        for key, value in dto.values.items():
            setattr(model, key, value)

@dataclass(frozen=True)
class DiscountSeasonShortViewDTO(ShortViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("start", "Начало"),
            FieldView("end", "Конец"),
            FieldView("duration", "Продолжительность")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(DiscountPeriodModel).filter(
            DiscountPeriodModel.id == id
        ).one_or_none()

        if model == None:
            return None
        
        duration = (model.end - model.start).days

        dto = DiscountSeasonShortViewDTO(id, values={
            "id": model.id,
            "start": date.strftime(model.start, "%d/%m/%Y"),
            "end": date.strftime(model.end, "%d/%m/%Y"),
            "duration": f"{duration} дней"
        })

        return dto

@dataclass(frozen=True)
class DiscountSeasonLongViewDTO(LongViewDTO):
    @classmethod
    def get_fields(cls):
        return DiscountSeasonShortViewDTO.get_fields()

    @classmethod
    def get_by_id(cls, session: Session, id):
        return DiscountSeasonShortViewDTO.get_by_id(session, id)
    
