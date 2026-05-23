from bson import ObjectId
from bson.errors import InvalidId


def parse_id(id_str):
    """Convierte el identificador a ObjectId cuando es posible.

    Esto permite almacenar _id tanto como cadenas UUID como ObjectId.
    """
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError, ValueError):
        return id_str
