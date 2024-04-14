from pymongo import MongoClient

class User:
    _db = None

    @classmethod
    def get_database(cls):
        return cls._db
    
    @classmethod
    def set_database(cls, db):
        cls._db = db

    def __init__(self, firstname: str, lastname: str, document_id: str, phone: str, birthdate: str, email: str):
        self.firstname: str = firstname
        self.lastname: str = lastname
        self.document_id: str = document_id
        self.phone: str = phone
        self.birthdate: str = birthdate
        self.email: str = email

    def create(self):
        user_data = {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "document_id": self.document_id,
            "phone": self.phone,
            "birthdate": self.birthdate,
            "email": self.email
        }

        return self._db.users.insert_one(user_data).inserted_id
         
    
    def delete(self):
        return self._db.users.delete_one({"document_id": self.document_id})
    
    @staticmethod
    def find_by_name(firstname: str, lastname: str):
        return User._db.users.find_one({"firstname": firstname, "lastname": lastname})
    
    @staticmethod
    def find_by_document(document_id: str):
        return User._db.users.find_one({"document_id": document_id})