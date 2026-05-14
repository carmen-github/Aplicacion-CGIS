from pydantic import BaseModel, Field, field_validator


class TensionViewSchema(BaseModel):
    """Validación de formulario (vista): solo comprueba presencia y formato básico."""
    id_paciente: str = Field(..., min_length=1)
    estado: str = Field(..., min_length=1)
    fecha: str = Field(..., min_length=1)
    valoracion: str = Field(..., min_length=1)
    valor_en_rango: bool

    @field_validator('fecha')
    @classmethod
    def validar_formato_fecha(cls, v):
        """Solo valida que el formato sea correcto, no aplica reglas de negocio."""
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}', v.strip()):
            raise ValueError("La fecha debe empezar con el formato YYYY-MM-DD.")
        return v.strip()
