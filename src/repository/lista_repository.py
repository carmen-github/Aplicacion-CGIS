import uuid
from bson import ObjectId
from bson.errors import InvalidId


def _parse_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        return id_str


class ListaRepository:
    """Repositorio de acceso a datos para la lista de servicios."""

    def __init__(self, db_connection):
        self.collection = db_connection.get_collection('listas')

    def insert(self, data: dict) -> dict:
        data = dict(data)
        data['_id'] = str(uuid.uuid4())
        self.collection.insert_one(data)
        return data

    def find_all(self) -> list:
        return list(self.collection.find())

    def find_by_id(self, id) -> dict | None:
        return self.collection.find_one({'_id': _parse_id(id)})

    def find_by_patient_id(self, id_paciente) -> list:
        return list(self.collection.find({'id_paciente': id_paciente}))

    def update(self, id, data: dict):
        update_data = {k: v for k, v in data.items() if k != '_id'}
        self.collection.update_one({'_id': _parse_id(id)}, {'$set': update_data})

    def delete(self, id):
        self.collection.delete_one({'_id': _parse_id(id)})
