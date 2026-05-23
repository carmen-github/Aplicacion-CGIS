from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class ListaAltaSchema(BaseModel):
    id_paciente: Annotated[str, Field(min_length=1)]
    fechaHora: Annotated[str, Field(min_length=1)]
    servicio: Annotated[str, Field(min_length=1)]
    estado: Annotated[str, Field(min_length=1)]
    patron: Annotated[str, Field()]
    repeticiones: Annotated[int, Field(ge=1)]

    @field_validator('servicio')
    @classmethod
    def validar_servicio(cls, v):
        if v.lower() not in ('Consulta', 'Enfermeria'):
            raise ValueError("El servicio debe ser 'Consulta' o 'Enfermeria'.")
        return v.lower()

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        v = v.lower()
        if v not in ('Pendiente', 'Atendido', 'Anulado'):
            raise ValueError("El estado debe ser: Pendiente, Atendido o Anulado.")
        return v

    @field_validator('patron')
    @classmethod
    def validar_patron(cls, v):
        v = v.lower()
        if v not in ('Unico', 'Diario', 'Semanal'):
            raise ValueError("El patrón debe ser: Unico, Diario o Semanal.")
        return v

    @field_validator('fechaHora')
    @classmethod
    def validar_fecha_hora(cls, v):
        try:
            raw = str(v).strip()
            if ' ' in raw and 'T' not in raw:
                raw = raw.replace(' ', 'T')
            datetime.fromisoformat(raw)
        except ValueError:
            raise ValueError("La fecha y hora debe tener formato ISO, por ejemplo YYYY-MM-DD HH:MM.")
        return v

    @field_validator('repeticiones')
    @classmethod
    def validar_repeticiones(cls, v, info):
        if v < 1:
            raise ValueError("El número de repeticiones debe ser 1 o mayor.")
        patron = info.data.get('patron', 'unico')
        if patron == 'unico' and v != 1:
            raise ValueError("Solo se puede repetir cuando el patrón es diario o semanal.")
        return v
