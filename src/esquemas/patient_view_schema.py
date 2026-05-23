from typing import Annotated
from pydantic import BaseModel, Field, field_validator


class PatientViewSchema(BaseModel):
    """Validación de formulario (vista): solo comprueba presencia y formato básico."""
    nombre: Annotated[str, Field(min_length=1)]
    apellido: Annotated[str, Field(min_length=1)]
    genero: Annotated[str, Field(min_length=1)]
    fechaNacimiento: Annotated[str, Field(min_length=1)]

    @field_validator('fechaNacimiento')
    @classmethod
    def validar_formato_fecha(cls, v):
        """Solo valida que el formato sea correcto, no aplica reglas de negocio."""
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v.strip()):
            raise ValueError("La fecha debe tener el formato YYYY-MM-DD.")
        return v.strip()
