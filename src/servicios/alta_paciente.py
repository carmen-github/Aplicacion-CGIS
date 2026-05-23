from pydantic import ValidationError
from esquemas.patient_alta_schema import PatientAltaSchema
from servicios.error_utils import extraer_errores


class AltaPaciente:
    """Servicio para dar de alta (crear) un paciente."""

    def __init__(self, patient_repository):
        self.repository = patient_repository

    def ejecutar(self, nombre, apellido, genero, fechaNacimiento) -> dict:
        """Valida y crea un paciente. Devuelve el dict con _id asignado.
        Raises ValueError si la validación falla.
        """
        try:
            schema = PatientAltaSchema(
                nombre=nombre, apellido=apellido,
                genero=genero, fechaNacimiento=fechaNacimiento
            )
        except ValidationError as e:
            raise ValueError('\n'.join(extraer_errores(e)))
        
        existente = self.repository.find_duplicate(
            schema.nombre, schema.apellido, schema.genero, schema.fechaNacimiento
        )
        if existente:
            raise ValueError("No se puede crear: Ya existe un paciente con los mismos datos.")

        return self.repository.insert(schema.model_dump())
