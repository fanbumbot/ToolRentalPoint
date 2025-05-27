from dataclasses import dataclass
from typing import Callable, Union
from enum import Enum

from abc import ABC

from sqlalchemy.orm import Session

class FieldValidationError(Exception):
    def __init__(self, message: str, key: str = None):
        self.message = message
        self.key = key

class FormErrors(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors

@dataclass(frozen=True)
class FieldView:
    id: str
    label: str

@dataclass(frozen=True)
class FieldInput(FieldView):
    convert_func: Callable[[str, object, Session], object] = None

@dataclass(frozen=True)
class FieldEnum(FieldView):
    options: list[FieldView]

class FieldDateInput(FieldInput):
    date_input: bool = True

class FieldCheckbox(FieldInput):
    is_checkbox: bool = True

class FieldFile(FieldInput):
    is_file: bool = True

class FieldTextArea(FieldInput):
    textarea: bool = True

class Fields:
    def __init__(self, fields: list[FieldView]):
        fields_dict: dict[str, FieldView] = dict()
        
        for field in fields:
            fields_dict[field.id] = field

        self.fields_dict = fields_dict

    def __iter__(self):
        return self.fields_dict.values().__iter__()
    
    def __getitem__(self, key: str):
        return self.fields_dict[key]

@dataclass(frozen=True)
class CreateDTO(ABC):
    values: dict[str, object]

    @classmethod
    def _get_values_for_model_by_data(cls, session: Session, data: dict[str, object]):
        models_args = dict()
        fields = cls.get_fields()

        errors = dict()
        
        for key, value in data.items():
            try:
                field = fields[key]
                field: FieldInput

                if field.convert_func != None:
                    converted_value = field.convert_func(key, value, session)
                else:
                    converted_value = value
                models_args[key] = converted_value
            except FieldValidationError as error:
                errors[error.key] = error.message
        if len(errors) != 0:
            raise FormErrors(errors)
        
        for field in fields:
            if isinstance(field, FieldCheckbox):
                models_args[field.id] = field.id in data

        return models_args
    
    @classmethod
    def get_model_by_data(cls, session: Session, data: dict[str, object]):
        raise NotImplementedError
    
    @classmethod
    def create_by_data(cls, session: Session, data: dict[str, object]):
        model = cls.get_model_by_data(session, data)
        session.add(model)
        session.flush([model])
        return model

    @classmethod
    def get_fields(cls) -> list[FieldInput]:
        raise NotImplementedError

    @classmethod
    def get(cls):
        raise NotImplementedError

@dataclass(frozen=True)
class EditDTO:
    id: int
    values: dict[str, object]

    @classmethod
    def update(cls, id, session: Session, data: dict[str, object]):
        raise NotImplementedError

    def get_value(self, id: str):
        return self.values[id]

    @classmethod
    def get_fields(cls) -> list[FieldInput]:
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, session, id):
        raise NotImplementedError
    
    @classmethod
    def get(cls, id, session: Session, data: dict[str, object]):
        values = dict()

        fields = cls.get_fields()

        errors = dict()

        for key, value in data.items():
            try:
                field = fields[key]
                field: FieldInput
                if field.convert_func != None:
                    converted_value = field.convert_func(key, value, session)
                else:
                    converted_value = value
                values[key] = converted_value
            except FieldValidationError as error:
                errors[error.key] = error.message

        if len(errors) != 0:
            raise FormErrors(errors)

        dto = cls(id, values)
        return dto

@dataclass(frozen=True)
class ShortViewDTO:
    id: int
    values: dict[str, object]

    def get_value(self, id: str):
        return self.values[id]

    @classmethod
    def get_fields(cls) -> list[FieldInput]:
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, session, id):
        raise NotImplementedError

@dataclass(frozen=True)
class LongViewDTO:
    id: int
    values: dict[str, object]

    def get_value(self, id: str):
        return self.values[id]

    @classmethod
    def get_fields(cls) -> list[FieldInput]:
        raise NotImplementedError

    @classmethod
    def get_by_id(cls, session, id):
        raise NotImplementedError