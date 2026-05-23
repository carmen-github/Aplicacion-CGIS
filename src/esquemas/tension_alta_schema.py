from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class TensionAltaSchema(BaseModel):
    """Validación de alta (negocio): reglas completas antes de persistir."""
    id_paciente: Annotated[str, Field(min_length=1)]
    estado: str
    fecha: str
    valoracion: Annotated[str, Field(min_length=1)]
    valor_en_rango: bool
    valores: dict = Field(default_factory=dict)

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        fhir_states = ('registered', 'preliminary', 'final', 'amended', 'corrected', 'cancelled', 'entered-in-error', 'unknown')
        if v.lower() not in fhir_states:
            raise ValueError(f"El estado debe ser uno de: {', '.join(fhir_states)}.")
        return v.lower()

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v):
        try:
            fecha_obj = datetime.fromisoformat(str(v).replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("La fecha no tiene un formato válido.")
        if fecha_obj > datetime.now(fecha_obj.tzinfo if hasattr(fecha_obj, 'tzinfo') else None):
            raise ValueError("La fecha no puede ser futura.")
        return v
