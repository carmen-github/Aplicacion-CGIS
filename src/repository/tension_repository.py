import uuid
from bson import ObjectId
from bson.errors import InvalidId


def _parse_id(id_str):
    """Retrocompatibilidad: intenta ObjectId, si falla usa el string (UUID)."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        return id_str


class TensionRepository:
    """Repositorio de acceso a datos para tensiones. Trabaja con dicts."""

    def __init__(self, db_connection):
        self.collection = db_connection.get_collection('tensiones')

    def insert(self, data: dict) -> dict:
        """Inserta una tensión con UUID como _id. Devuelve el dict con _id asignado."""
        data = dict(data)
        data['_id'] = str(uuid.uuid4())
        self.collection.insert_one(data)
        return data

    def find_all(self) -> list:
        """Devuelve todas las tensiones como lista de dicts."""
        return list(self.collection.find())

    def find_by_id(self, id) -> dict | None:
        """Busca una tensión por su _id. Devuelve dict o None."""
        return self.collection.find_one({'_id': _parse_id(id)})

    def find_by_patient_id(self, id_paciente) -> list:
        """Devuelve todas las tensiones de un paciente dado."""
        return list(self.collection.find({'id_paciente': id_paciente}))

    def update(self, id, data: dict):
        """Actualiza una tensión existente (excluye _id del $set)."""
        update_data = {k: v for k, v in data.items() if k != '_id'}
        self.collection.update_one({'_id': _parse_id(id)}, {'$set': update_data})

    def delete(self, id):
        """Elimina una tensión por su _id."""
        self.collection.delete_one({'_id': _parse_id(id)})
