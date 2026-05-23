class BajaLista:
    """Servicio para dar de baja elementos de la lista de servicios."""

    def __init__(self, lista_repository):
        self.repository = lista_repository

    def ejecutar(self, id):
        self.repository.delete(id)
