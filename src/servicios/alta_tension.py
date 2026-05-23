from pydantic import ValidationError
from esquemas.tension_alta_schema import TensionAltaSchema
from servicios.error_utils import extraer_errores


class AltaTension:
    """Servicio para dar de alta (crear) una tensión."""

    def __init__(self, tension_repository):
        self.repository = tension_repository

    def ejecutar(self, id_paciente, estado, fecha, valoracion, valor_en_rango, valores=None) -> dict:
        """Valida y crea una tensión. Devuelve el dict con _id asignado.
        Raises ValueError si la validación falla.
        """
        try:
            schema = TensionAltaSchema(
                id_paciente=id_paciente, estado=estado,
                fecha=fecha, valoracion=valoracion,
                valor_en_rango=valor_en_rango,
                valores=valores or {}
            )
        except ValidationError as e:
            raise ValueError('\n'.join(extraer_errores(e)))
        data = schema.model_dump()
        return self.repository.insert(data)
