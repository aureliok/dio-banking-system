from pymongo import MongoClient
from decimal import Decimal
from typing import List

from app.models.user import User
from utils.AccountIdGenerator import AccountIdGenerator
from utils.static_vars import MONGODB_PATH

class Account:
    _db = None

    @classmethod
    def get_database(cls):
        return cls._db
    
    @classmethod
    def set_database(cls, db):
        cls._db = db

    def __init__(self, user_document: str, balance: Decimal=0, is_frozen: bool=False, account_id: str=None):
        self.account_id: str = account_id
        self.user_document: str = user_document
        self.balance: Decimal = balance
        self.is_frozen: bool = is_frozen
        self.transaction_history = List[dict] = []


    def create(self) -> int:
        User.set_database(self._db)
        user = User.find_by_document(self.user_document)

        if user is None:
            raise Exception("The client is not registered")
        
        self.account_id = AccountIdGenerator.generate(self._db)

        account_data = {
            "account_id": self.account_id,
            "user_document": self.user_document,
            "balance": self.balance,
            "is_frozen": self.is_frozen
        }

        with MongoClient(MONGODB_PATH).start_session() as session:
            with session.start_transaction():
                inserted_id = self._db.accounts.insert_one(account_data).inserted_id

                session.commit_transaction()
        
        return inserted_id
    

    def delete(self) -> int:
        if self.balance > 0:
            return 0
        
        delete_result = self._db.accounts.delete_one({"account_id": self.account_id})
        return delete_result.deleted_count


    def freeze(self) -> None:
        self.is_frozen = True
        self._db.accounts.update_one({"account_id": self.account_id},
                                     {"$set": {"is_frozen": self.is_frozen}})

    
    def unfreeze(self) -> None:
        self.is_frozen = False
        self._db.accounts.update_one({"account_id": self.account_id},
                                     {"$set": {"is_frozen": self.is_frozen}})
        
    
    def balance_check(self) -> Decimal:
        return self.balance

    
    def deposit(self, value) -> None:
        self.balance += value
        self._db.accounts.update_one({"account_id": self.account_id},
                                     {"$set": {"balance": self.balance}})


    def withdraw(self, value) -> None:
        if value > self.balance:
            return
        
        self.balance -= value
        self._db.accounts.update_one({"account_id": self.account_id},
                                     {"$set": {"balance": self.balance}})
        
    
    def transfer(self, to_account, value) -> None:
        if value > self.balance:
            return
        
        with MongoClient(MONGODB_PATH).start_session() as session:
            with session.start_transaction():
                recipient = Account.find_by_account_id(to_account)
                self.balance -= value
                recipient["balance"] += value

                self._db.accounts.update_one({"account_id": self.account_id},
                                             {"$set": {"balance": self.balance}})
                
                self._db.accounts.update_one({"account_id": recipient["account_id"]},
                                             {"$set": {"balance": recipient["balance"]}})
                
                session.commit_transaction()


    def add_transaction(self):
        pass


    def get_transaction_history(self):
        pass
                
        
    @staticmethod
    def find_by_account_id(account_id):
        return Account._db.accounts.find_one({"account_id": account_id})
    
    @staticmethod
    def find_by_document_id(document_id):
        return Account._db.accounts.find_one({"user_document": document_id}) 
    

