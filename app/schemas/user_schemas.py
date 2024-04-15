from dataclasses import dataclass

@dataclass
class UserData:
    firstname: str
    lastname: str
    document_id: str
    phone: str
    birthdate: str
    email: str

    def to_dict(self):
        return {
            "firstname": self.firstname,
            "lastname": self.lastname,
            "document_id": self.document_id,
            "phone": self.phone,
            "birthdate": self.birthdate,
            "email": self.email
        }

@dataclass
class UserUpdate:
    document_id: str
    phone: str
    email: str

    def to_dict(self):
        return {
            "document_id": self.document_id,
            "phone": self.phone,
            "email": self.email
        }
