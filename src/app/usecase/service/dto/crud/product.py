from sqlalchemy import and_

from fastapi import UploadFile, File

from .base.crud_base_dto import *

import re
import os

from .....infrastructure.models import ProductModel, CategoryModel

def convert_slug(key: str, slug, session: Session):
    regex = "^[a-z0-9_]{3,32}$"
    pattern = re.compile(regex)
    if not re.fullmatch(pattern, slug):
        raise FieldValidationError("Могут использоваться латинские буквы, цифры, '_'. Размер от 3 до 32 символов", key)

    return slug

def convert_category_id(key: str, category_id_str: str, session: Session):
    try:
        category_id = int(category_id_str)
    except:
        raise FieldValidationError("Не является целым числом", key)
    
    model = session.query(CategoryModel).filter(
        CategoryModel.id == category_id
    ).one_or_none()

    if model == None:
        raise FieldValidationError("Категории с таким ID не существует", key)
    return category_id

def convert_name(key: str, name: str, session: Session):
    if len(name) < 1 or len(name) > 64:
        raise FieldValidationError("Название товара должно быть от 1 до 64 символов", key)
    return name

def convert_image(key: str, image_file: UploadFile, session: Session):
    return image_file

def convert_cost(key: str, cost_str: str, session: Session):
    try:
        cost = int(cost_str)
    except:
        raise FieldValidationError("Не является целым числом", key)

    if cost < 0:
        raise FieldValidationError("Должно быть неотрицательным", key)
    
    return cost

def convert_period(key: str, days_str: str, session: Session):
    if days_str.strip() == "":
        return None
    try:
        days = int(days_str)
    except:
        raise FieldValidationError("Не является целым числом", key)
    
    if days <= 0:
        raise FieldValidationError("Должно быть положительным", key)

    return days

def convert_is_active(key: str, is_active_str: str, session: Session):
    return is_active_str

def convert_is_for_rent(key: str, is_for_rent_str: str, session: Session):
    return is_for_rent_str

def update_image(name: str, image: UploadFile):
    output_file_path = f"static/images/{name}"
    file_path = "app/" + output_file_path
    if image.size == 0:
        return output_file_path

    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, "wb") as buffer:
        buffer.write(image.file.read())

    return output_file_path

@dataclass(frozen=True)
class ProductCreateDTO(CreateDTO):
    @classmethod
    def get_model_by_data(cls, session: Session, data: dict[str, object]):
        args = cls._get_values_for_model_by_data(session, data)
        model = ProductModel(**args)
        return model
    
    @classmethod
    def create_by_data(cls, session, data):
        model = cls.get_model_by_data(session, data)

        if ((model.standard_rental_period == None and model.is_for_rent_or_sale) or
            (model.standard_rental_period != None and not model.is_for_rent_or_sale)):
            
            raise FieldValidationError("Если товар для аренды - необходимо указывать срок аренды\nЕсли для покупки - нельзя указывать срок аренды")

        check_model = session.query(ProductModel).filter(
            ProductModel.slug == data["slug"]
        ).one_or_none()

        if check_model != None:
            raise FieldValidationError("Товар с таким слагом уже существует")

        file_path = update_image(model.slug, model.image)
        model.image = file_path

        session.add(model)
        session.flush([model])

        return model

    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("slug", "Слаг", convert_slug),
            FieldInput("category_id", "ID категории", convert_category_id),
            FieldInput("name", "Название", convert_name),
            FieldInput("description", "Описание"),
            FieldFile("image", "Картинка", convert_image),
            FieldInput("rent_or_buy_cost", "Цена", convert_cost),
            FieldInput("standard_rental_period", "Период оплаты (в днях)", convert_period),
            FieldCheckbox("is_for_rent_or_sale", "Для аренды (иначе - для продажи)", convert_is_for_rent),
        ])

    @classmethod
    def get(cls):
        return ProductCreateDTO()

@dataclass(frozen=True)
class ProductEditDTO(EditDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldInput("slug", "Слаг", convert_slug),
            FieldInput("category_id", "ID категории", convert_category_id),
            FieldInput("name", "Название", convert_name),
            FieldInput("description", "Описание"),
            FieldFile("image", "Картинка", convert_image),
            FieldInput("rent_or_buy_cost", "Цена", convert_cost),
            FieldInput("standard_rental_period", "Период оплаты (в днях)", convert_period),
            FieldCheckbox("is_active", "Активный", convert_is_active),
            FieldCheckbox("is_for_rent_or_sale", "Для аренды (иначе - для продажи)", convert_is_for_rent),
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(ProductModel).filter(
            ProductModel.id == id
        ).one_or_none()

        if model == None:
            return None
        
        dto = ProductEditDTO(id, values={
            "slug": model.slug,
            "category_id": model.category_id,
            "name": model.name,
            "description": model.description,
            "image": model.image,
            "rent_or_buy_cost": model.rent_or_buy_cost,
            "standard_rental_period": model.standard_rental_period if model.standard_rental_period else "",
            "is_active": model.is_active,
            "is_for_rent_or_sale": model.is_for_rent_or_sale
        })

        return dto

    @classmethod
    def update(cls, id, session: Session, data):
        dto = cls.get(id, session, data)

        check_model = session.query(ProductModel).filter(
            and_(
                ProductModel.id != id,
                ProductModel.slug == data["slug"]
            )
        ).one_or_none()

        if check_model != None:
            raise FieldValidationError("Товар с таким слагом уже существует")

        model = session.query(ProductModel).filter(
            ProductModel.id == id
        ).one_or_none()

        if model == None:
            raise FieldValidationError("Товар для изменения не найден")

        if ((data["standard_rental_period"] == "" and "is_for_rent_or_sale" in data) or
            (data["standard_rental_period"] != "" and "is_for_rent_or_sale" not in data)):
            
            raise FieldValidationError("Если товар для аренды - необходимо указывать срок аренды\nЕсли для покупки - нельзя указывать срок аренды")

        file_path = update_image(model.slug, data["image"])

        setattr(model, "is_for_rent_or_sale", False)
        setattr(model, "is_active", False)
        for key, value in dto.values.items():
            if key == "is_for_rent_or_sale":
                setattr(model, key, True)
            elif key == "is_active":
                setattr(model, key, True)
            else:
                setattr(model, key, value)

        model.image = file_path

@dataclass(frozen=True)
class ProductShortViewDTO(ShortViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("name", "Название")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(ProductModel).filter(
            ProductModel.id == id
        ).one_or_none()

        if model == None:
            return

        dto = ProductShortViewDTO(id, values={
            "id": id,
            "name": model.name
        })

        return dto

@dataclass(frozen=True)
class ProductLongViewDTO(LongViewDTO):
    @classmethod
    def get_fields(cls):
        return Fields([
            FieldView("id", "ID"),
            FieldView("slug", "Слаг"),
            FieldView("category_id", "ID категории"),
            FieldView("name", "Название"),
            FieldView("description", "Описание"),
            FieldView("image", "Картинка"),
            FieldView("rent_or_buy_cost", "Цена"),
            FieldView("standard_rental_period", "Период оплаты (в днях)"),
            FieldView("is_for_rent_or_sale", "Для продажи или для аренды"),
            FieldView("is_active", "Активный")
        ])

    @classmethod
    def get_by_id(cls, session: Session, id):
        model = session.query(ProductModel).filter(
            ProductModel.id == id
        ).one_or_none()

        if model == None:
            return

        dto = ProductShortViewDTO(id, values={
            "id": id,
            "slug": model.slug,
            "name": model.name,
            "category_id": model.category_id,
            "name": model.name,
            "description": model.description,
            "image": model.image,
            "rent_or_buy_cost": model.rent_or_buy_cost,
            "standard_rental_period": model.standard_rental_period if model.standard_rental_period else "-",
            "is_for_rent_or_sale": "Для аренды" if model.is_for_rent_or_sale else "Для продажи",
            "is_active": "Да" if model.is_active else "Нет"
        })

        return dto