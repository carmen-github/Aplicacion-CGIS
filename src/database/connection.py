from pymongo import MongoClient

class DatabaseConnection:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['mi_app']

    def get_collection(self, name):
        return self.db[name]