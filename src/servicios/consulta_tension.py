class ConsultaTension:
    """Servicio para consultar tensiones."""

    def __init__(self, tension_repository):
        self.repository = tension_repository

    def obtener_todas(self):
        """Devuelve todas las tensiones."""
        return self.repository.find_all()

    def obtener_por_id(self, id):
        """Busca una tensión por su _id. Devuelve Tension o None."""
        return self.repository.find_by_id(id)

    def obtener_por_paciente(self, id_paciente):
        """Devuelve todas las tensiones de un paciente dado."""
        return self.repository.find_by_patient_id(id_paciente)
