from pymongo import MongoClient
from datetime import datetime
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

    def __init__(self, user_document: str, balance: Decimal=0, 
                 is_frozen: bool=False, account_id: str=None, 
                 last_date_transactions_count: int=0, 
                 last_date_transaction: str=datetime.today().strftime("%d-%m-%Y")):
        
        self.account_id: str = account_id
        self.user_document: str = user_document
        self.balance: float = balance
        self.is_frozen: bool = is_frozen
        self.transaction_history: List[dict] = []
        self.last_date_transactions_count: int = last_date_transactions_count
        self.last_date_transaction: str = last_date_transaction


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
            "is_frozen": self.is_frozen,
            "last_date_transactions_count": self.last_date_transactions_count,
            "last_date_transaction": self.last_date_transaction
        }

        with MongoClient(MONGODB_PATH).start_session() as session:
            with session.start_transaction():
                inserted_id = self._db.accounts.insert_one(account_data).inserted_id
                self._db.transactions_history.insert_one({
                    "account_id": self.account_id,
                    "transactions": self.transaction_history
                })

                session.commit_transaction()
        
        return inserted_id
    

    def delete(self) -> int:
        if Decimal(self.balance) > 0:
            return 0
        
        print(self.account_id)
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
        
    
    def balance_check(self) -> float:
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
        
    
    def transfer(self, to_account: str, value) -> None:
        if value > self.balance:
            return
        
        with MongoClient(MONGODB_PATH).start_session() as session:
            with session.start_transaction():
                recipient = Account.find_by_account_id(to_account)
                self.balance -= value
                recipient.balance += value

                self._db.accounts.update_one({"account_id": self.account_id},
                                             {"$set": {"balance": self.balance}})
                
                self._db.accounts.update_one({"account_id": recipient.account_id},
                                             {"$set": {"balance": recipient.balance}})
                
                session.commit_transaction()


    def add_transaction(self, transaction_type: str, value: float=None, counterpart: str=None, transaction_time: str=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        transaction_data = {
            "timestamp": datetime.strptime(transaction_time, "%Y-%m-%d %H:%M:%S"),
            "type": transaction_type,
            "value": value,
            "counterpart": counterpart
        }

        self.transaction_history.append(transaction_data)
        self._db.transactions_history.update_one({"account_id": self.account_id},
                                                  {"$push": {"transactions": transaction_data}},
                                                  upsert=True)


    def get_transaction_history(self):
        transactions = self._db.transactions_history.find_one({"account_id": self.account_id})
        return [t for t in transactions["transactions"]]
    

    def update_transaction_count(self, transaction_datetime: str):
        transaction_date = datetime.strptime(transaction_datetime, "%Y-%m-%d %H:%M:%S")
        if self.last_date_transaction == transaction_date:
            self.last_date_transactions_count += 1
        else:
            self.last_date_transactions_count = 1

        self._db.accounts.update_one({"user_document": self.user_document},
                                     {"$set": {"last_date_transactions_count": self.last_date_transactions_count,
                                               "last_date_transaction": transaction_date}})
                
        
    @staticmethod
    def find_by_account_id(account_id):
        account =  Account._db.accounts.find_one({"account_id": account_id})
        if account:
            del account["_id"]
            return Account(**account)
        
        return None

    
    @staticmethod
    def find_by_document_id(document_id):
        account = Account._db.accounts.find_one({"user_document": document_id}) 
        if account:
            del account["_id"]
            return Account(**account)
        
        return None
            
    

