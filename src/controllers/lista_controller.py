from repository.lista_repository import ListaRepository
from servicios.alta_lista import AltaLista
from servicios.baja_lista import BajaLista
from servicios.modificacion_lista import ModificacionLista
from servicios.consulta_lista import ConsultaLista


class ListaController:
    """Controlador de la entidad Lista. Orquesta operaciones CRUD y cambios de estado."""

    def __init__(self, db_connection):
        repository = ListaRepository(db_connection)
        self.alta = AltaLista(repository)
        self.baja = BajaLista(repository)
        self.modificacion = ModificacionLista(repository)
        self.consulta = ConsultaLista(repository)

    def create(self, id_paciente, fechaHora, servicio, estado, patron, repeticiones):
        return self.alta.ejecutar(id_paciente, fechaHora, servicio, estado, patron, repeticiones)

    def read_all(self):
        return self.consulta.obtener_todos()

    def read_by_id(self, id):
        return self.consulta.obtener_por_id(id)

    def read_by_patient(self, id_paciente):
        return self.consulta.obtener_por_paciente(id_paciente)

    def update(self, id, data: dict):
        self.modificacion.ejecutar(id, data)

    def delete(self, id):
        self.baja.ejecutar(id)

    def update_state(self, id, estado):
        self.modificacion.ejecutar(id, {'estado': estado})
