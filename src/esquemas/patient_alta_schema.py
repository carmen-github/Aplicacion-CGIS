from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class PatientAltaSchema(BaseModel):
    """Validación de alta (negocio): reglas completas antes de persistir."""
    nombre: Annotated[str, Field(min_length=2)]
    apellido: Annotated[str, Field(min_length=2)]
    genero: str
    fechaNacimiento: str

    @field_validator('genero')
    @classmethod
    def validar_genero(cls, v):
        if v.lower() not in ('masculino', 'femenino', 'otro'):
            raise ValueError("El género debe ser: masculino, femenino, otro.")
        return v.lower()

    @field_validator('fechaNacimiento')
    @classmethod
    def validar_fecha(cls, v):
        try:
            dt = datetime.strptime(str(v), '%Y-%m-%d')
        except ValueError:
            raise ValueError("La fecha de nacimiento debe tener el formato YYYY-MM-DD.")
        if dt > datetime.now():
            raise ValueError("La fecha de nacimiento debe ser menor a la fecha actual.")
        return v
