from datetime import datetime, timedelta
from pydantic import ValidationError
from esquemas.lista_alta_schema import ListaAltaSchema
from servicios.error_utils import extraer_errores


class AltaLista:
    """Servicio para dar de alta elementos de la lista de servicios."""

    def __init__(self, lista_repository):
        self.repository = lista_repository

    def ejecutar(self, id_paciente, fechaHora, servicio, estado, patron, repeticiones):
        try:
            schema = ListaAltaSchema(
                id_paciente=id_paciente,
                fechaHora=fechaHora,
                servicio=servicio,
                estado=estado,
                patron=patron,
                repeticiones=repeticiones,
            )
        except ValidationError as e:
            raise ValueError('\n'.join(extraer_errores(e)))

        data = schema.model_dump()
        base_date = datetime.fromisoformat(str(data['fechaHora']).replace(' ', 'T'))
        items = []
        delta = timedelta(days=1) if data['patron'] == 'diario' else timedelta(days=7) if data['patron'] == 'semanal' else timedelta(days=0)

        for index in range(data['repeticiones']):
            item = dict(data)
            item['fechaHora'] = base_date.isoformat()
            items.append(self.repository.insert(item))
            base_date = base_date + delta

        return items[0] if len(items) == 1 else items
