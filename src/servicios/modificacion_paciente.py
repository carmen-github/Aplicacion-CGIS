from pydantic import ValidationError
from esquemas.patient_alta_schema import PatientAltaSchema
from servicios.error_utils import extraer_errores


class ModificacionPaciente:
    """Servicio para modificar (actualizar) un paciente existente."""

    def __init__(self, patient_repository):
        self.repository = patient_repository

    def ejecutar(self, id, data: dict):
        """Valida y actualiza un paciente existente.
        Raises ValueError si la validación falla.
        """
        try:
            schema = PatientAltaSchema(
                nombre=data.get('nombre', ''),
                apellido=data.get('apellido', ''),
                genero=data.get('genero', data.get('género', '')),
                fechaNacimiento=data.get('fechaNacimiento', '')
            )
        except ValidationError as e:
            raise ValueError('\n'.join(extraer_errores(e)))
        self.repository.update(id, schema.model_dump())
