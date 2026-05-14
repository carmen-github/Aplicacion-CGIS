from repository.patient_repository import PatientRepository
from servicios.alta_paciente import AltaPaciente
from servicios.baja_paciente import BajaPaciente
from servicios.modificacion_paciente import ModificacionPaciente
from servicios.consulta_paciente import ConsultaPaciente


class PatientController:
    """Controlador de pacientes. Orquesta los servicios para cada operación.
    Trabaja con dicts en lugar de objetos Patient.
    """

    def __init__(self, db_connection):
        repository = PatientRepository(db_connection)
        self.alta = AltaPaciente(repository)
        self.baja = BajaPaciente(repository)
        self.modificacion = ModificacionPaciente(repository)
        self.consulta = ConsultaPaciente(repository)

    def create(self, nombre, apellido, genero, fechaNacimiento) -> dict:
        """Dar de alta un paciente. Devuelve el dict creado."""
        return self.alta.ejecutar(nombre, apellido, genero, fechaNacimiento)

    def read_all(self) -> list:
        """Consultar todos los pacientes como lista de dicts."""
        return self.consulta.obtener_todos()

    def read_by_id(self, id) -> dict | None:
        """Consultar un paciente por su _id. Devuelve dict o None."""
        return self.consulta.obtener_por_id(id)

    def update(self, id, data: dict):
        """Modificar un paciente existente a partir de un dict de datos."""
        self.modificacion.ejecutar(id, data)

    def delete(self, id):
        """Dar de baja un paciente."""
        self.baja.ejecutar(id)