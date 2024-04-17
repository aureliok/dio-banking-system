from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas.user_schemas import UserData, UserUpdate
from app.api.services.user_service import UserService

from utils.static_vars import MONGODB_PATH
from app.database.mongodb import MongoClient

client = MongoClient(MONGODB_PATH)
db = client.bank

router = APIRouter()


class UserAPI:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    
    async def create_user(self, user_data: UserData):
        self.user_service.create_user(user_data)


    async def update_user(self, user_update: UserUpdate):
        self.user_service.update_user(user_update)
    

    async def delete_user(self, user_data: UserData):
        self.user_service.delete_user(user_data)
    
    
    async def get_user_info(self, user_data: UserData):
        return self.user_service.get_user_info(user_data.document_id).to_dict()
        
