from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Annotated

from pydantic import BaseModel, Field


class ObservationState(str, Enum):
    REGISTERED = 'registered'
    PRELIMINARY = 'preliminary'
    FINAL = 'final'
    AMENDED = 'amended'
    CORRECTED = 'corrected'
    CANCELLED = 'cancelled'
    ENTERED_IN_ERROR = 'entered-in-error'
    UNKNOWN = 'unknown'

class ValoresLOINC(BaseModel):
    sistolica: int = Field(..., gt=0, lt=300)
    diastolica: int = Field(..., gt=0, lt=200)
    metodo: str = Field(default="Auscultatorio")
    sitio_cuerpo: str = Field(default="Brazo izquierdo")
    tamano_brazalete: str = Field(default="Adulto estandar")
    dispositivo: str = Field(default="Esfigmomanometro manual")


NonEmptyText = Annotated[str, Field(..., strip_whitespace=True, min_length=1)]


class Tension(BaseModel):
    id: Annotated[str, Field(..., alias='_id')]
    id_paciente: NonEmptyText
    estado: ObservationState
    fecha: date
    valoracion: NonEmptyText
    valor_en_rango: bool
    valores: ValoresLOINC

    model_config = {
        'populate_by_name': True,
        'json_schema_extra': {
            'example': {
                '_id': 'uuid-or-objectid',
                'id_paciente': 'patient-id',
                'estado': 'preliminary',
                'fecha': '2026-05-22',
                'valoracion': 'Normal',
                'valor_en_rango': True,
                'valores': {
                    'sistolica': 120,
                    'diastolica': 80,
                    'metodo': 'Auscultatorio',
                    'sitio_cuerpo': 'Brazo izquierdo',
                    'tamano_brazalete': 'Adulto estandar',
                    'dispositivo': 'Esfigmomanometro manual'
                },
            }
        }
    }
