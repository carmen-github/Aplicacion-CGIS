from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TensionAltaSchema(BaseModel):
    """Validación de alta (negocio): reglas completas antes de persistir."""
    id_paciente: str = Field(..., min_length=1)
    estado: str
    fecha: str
    valoracion: str = Field(..., min_length=1)
    valor_en_rango: bool

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v):
        if v.lower() not in ('preliminar', 'final', 'corregido'):
            raise ValueError("El estado debe ser: preliminar, final, corregido.")
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
