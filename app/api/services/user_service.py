from app.models.user import User
from app.schemas.user_schemas import *


class UserService:
    def __init__(self, db):
        self._db = db

    def create_user(self, user_data: UserData) -> None:
        user = User(**user_data.to_dict())
        user.create()
        

    def update_user(self, update_data: UserUpdate) -> None:
        user = User.find_by_document(update_data.document_id)

        update_data = {key:value for key, value in update_data.to_dict().items() if value is not None}
        user.update(update_data)


    def delete_user(self, user_data: UserData) -> None:
        user = User.find_by_document(user_data.document_id)

        for key,value in user.__dict__.items():
            if value != user_data.__dict__[key]:
                raise Exception("Couldn't verify client data")

        user.delete()


    def get_user_info(self, document_id: str) -> UserData:
        user = User.find_by_document(document_id)
        if not user:
            raise FileNotFoundError()

        return UserData(**user.__dict__)
        