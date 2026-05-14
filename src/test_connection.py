from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['myapp']
    # Test connection
    db.command('ping')
    print("Conexión exitosa a MongoDB")
    print("Bases de datos:", client.list_database_names())
    print("Colecciones en myapp:", db.list_collection_names())
except Exception as e:
    print("Error de conexión:", e)