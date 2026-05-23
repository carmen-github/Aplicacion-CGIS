class ConsultaLista:
    """Servicio para consultar los elementos de la lista de servicios."""

    def __init__(self, lista_repository):
        self.repository = lista_repository

    def obtener_todos(self):
        return self.repository.find_all()

    def obtener_por_id(self, id):
        return self.repository.find_by_id(id)

    def obtener_por_paciente(self, id_paciente):
        return self.repository.find_by_patient_id(id_paciente)
