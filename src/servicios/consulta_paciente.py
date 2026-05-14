class ConsultaPaciente:
    """Servicio para consultar pacientes."""

    def __init__(self, patient_repository):
        self.repository = patient_repository

    def obtener_todos(self):
        """Devuelve todos los pacientes."""
        return self.repository.find_all()

    def obtener_por_id(self, id):
        """Busca un paciente por su _id. Devuelve Patient o None."""
        return self.repository.find_by_id(id)
