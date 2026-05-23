from repository.tension_repository import TensionRepository
from servicios.alta_tension import AltaTension
from servicios.baja_tension import BajaTension
from servicios.modificacion_tension import ModificacionTension
from servicios.consulta_tension import ConsultaTension


class TensionController:
    """Controlador de tensiones. Orquesta los servicios para cada operación.
    Trabaja con dicts en lugar de objetos Tension.
    """

    def __init__(self, db_connection):
        repository = TensionRepository(db_connection)
        self.alta = AltaTension(repository)
        self.baja = BajaTension(repository)
        self.modificacion = ModificacionTension(repository)
        self.consulta = ConsultaTension(repository)

    def create(self, id_paciente, estado, fecha, valoracion, valor_en_rango, valores=None) -> dict:
        """Dar de alta una tensión. Devuelve el dict creado."""
        return self.alta.ejecutar(id_paciente, estado, fecha, valoracion, valor_en_rango, valores)

    def read_all(self) -> list:
        """Consultar todas las tensiones como lista de dicts."""
        return self.consulta.obtener_todas()

    def read_by_id(self, id) -> dict | None:
        """Consultar una tensión por su _id. Devuelve dict o None."""
        return self.consulta.obtener_por_id(id)

    def read_by_patient(self, id_paciente) -> list:
        """Consultar tensiones de un paciente dado."""
        return self.consulta.obtener_por_paciente(id_paciente)

    def update(self, id, data: dict):
        """Modificar una tensión existente a partir de un dict de datos."""
        self.modificacion.ejecutar(id, data)

    def delete(self, id):
        """Dar de baja una tensión."""
        self.baja.ejecutar(id)

    def study_by_patient(self, id_paciente, ultimas_n: int | None = None) -> dict:
        """Calcula un estudio de tensiones para un paciente."""
        return self.consulta.obtener_estudio_por_paciente(id_paciente, ultimas_n)
