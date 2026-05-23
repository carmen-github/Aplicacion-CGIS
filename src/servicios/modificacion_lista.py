from pydantic import ValidationError
from esquemas.lista_alta_schema import ListaAltaSchema
from servicios.error_utils import extraer_errores


class ModificacionLista:
    """Servicio para modificar elementos de la lista de servicios."""

    def __init__(self, lista_repository):
        self.repository = lista_repository

    def ejecutar(self, id, data: dict):
        existing = self.repository.find_by_id(id)
        if not existing:
            raise ValueError("No se encontró el elemento para actualizar.")

        payload = {
            'id_paciente': data.get('id_paciente', existing.get('id_paciente', '')),
            'fechaHora': data.get('fechaHora', existing.get('fechaHora', '')),
            'servicio': data.get('servicio', existing.get('servicio', '')),
            'estado': data.get('estado', existing.get('estado', 'pendiente')),
            'patron': data.get('patron', existing.get('patron', 'unico')),
            'repeticiones': data.get('repeticiones', existing.get('repeticiones', 1)),
        }

        try:
            schema = ListaAltaSchema(**payload)
        except ValidationError as e:
            raise ValueError('\n'.join(extraer_errores(e)))

        update_data = schema.model_dump()
        self.repository.update(id, update_data)
