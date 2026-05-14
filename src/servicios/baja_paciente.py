class BajaPaciente:
    """Servicio para dar de baja (eliminar) un paciente."""

    def __init__(self, patient_repository):
        self.repository = patient_repository

    def ejecutar(self, id):
        """Elimina un paciente por su _id.

        Args:
            id: identificador del paciente a eliminar.
        """
        self.repository.delete(id)
