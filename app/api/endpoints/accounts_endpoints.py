from fastapi import APIRouter, Depends, HTTPException
from app.models.account import Account
from app.schemas.account_schemas import *
from app.api.services.account_service import AccountService
from datetime import datetime
from utils.static_vars import MONGODB_PATH
from app.database.mongodb import MongoClient

client = MongoClient(MONGODB_PATH)
db = client.bank

router = APIRouter()


class AccountAPI:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service


    def create_account(self, account_data: AccountData):
        self.account_service.create_account(account_data)


    def delete_account(self, account_data: AccountData):
        self.account_service.delete_account(account_data)

    
    def freeze_account(self, account_data: AccountData):
        self.account_service.freeze_account(account_data)

    
    def unfreeze_account(self, account_data: AccountData):
        self.account_service.unfreeze_account(account_data)


    def check_balance(self, account_data: AccountData):
        print(self.account_service.check_balance(account_data))
        return {
            "balance": self.account_service.check_balance(account_data)
        }

    
    def deposit(self, account_data: AccountTransaction):
        self.account_service.deposit(account_data)


    def withdraw(self, account_data: AccountTransaction):
        self.account_service.withdraw(account_data)


    def transfer(self, account_transaction: AccountTransaction):
        self.account_service.transfer(account_transaction)


    def get_transactions_history(self, account_data: AccountHistoryRequest):
        return self.account_service.get_transactions_history(account_data)

    