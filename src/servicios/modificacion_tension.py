from pydantic import ValidationError
from esquemas.tension_alta_schema import TensionAltaSchema
from servicios.error_utils import extraer_errores


class ModificacionTension:
    """Servicio para modificar (actualizar) una tensión existente."""

    def __init__(self, tension_repository):
        self.repository = tension_repository

    def ejecutar(self, id, data: dict):
        """Valida y actualiza una tensión existente.
        Raises ValueError si la validación falla.
        """
        try:
            schema = TensionAltaSchema(
                id_paciente=data.get('id_paciente', ''),
                estado=data.get('estado', ''),
                fecha=data.get('fecha', ''),
                valoracion=data.get('valoracion', ''),
                valor_en_rango=data.get('valor_en_rango', False)
            )
        except ValidationError as e:
            raise ValueError('\n'.join(extraer_errores(e)))
        update_data = schema.model_dump()
        # Preserva el campo 'valores' si existía
        if 'valores' in data:
            update_data['valores'] = data['valores']
        self.repository.update(id, update_data)
