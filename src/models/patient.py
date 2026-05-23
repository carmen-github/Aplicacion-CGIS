from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MASCULINO = 'masculino'
    FEMENINO = 'femenino'
    OTRO = 'otro'

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            for member in cls:
                if member.value == normalized:
                    return member
        return super()._missing_(value)


NonEmptyText = Annotated[str, Field(..., strip_whitespace=True, min_length=1)]


class Patient(BaseModel):
    id: Annotated[str, Field(..., alias='_id')]
    nombre: NonEmptyText
    apellido: NonEmptyText
    genero: Gender
    fechaNacimiento: date

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                '_id': 'uuid-or-objectid',
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'genero': 'masculino',
                'fechaNacimiento': '1990-01-01',
            }
        }
    }

    def display_name(self) -> str:
        return f"{self.nombre} {self.apellido}"
