class BajaTension:
    """Servicio para dar de baja (eliminar) una tensión."""

    def __init__(self, tension_repository):
        self.repository = tension_repository

    def ejecutar(self, id):
        """Elimina una tensión por su _id.

        Args:
            id: identificador de la tensión a eliminar.
        """
        self.repository.delete(id)
