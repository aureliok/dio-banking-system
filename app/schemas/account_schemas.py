from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class AccountData:
    account_id: Optional[str]=None
    user_document: str=None
    balance: float=0
    is_frozen: bool=False
    transaction_history: List[dict]=None

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "user_document": self.user_document,
            "balance": self.balance,
            "is_frozen": self.is_frozen
        }
    

@dataclass
class AccountTransaction:
    account_id: Optional[str]=None
    user_document: str=None
    value: float=0
    recipient_account_id: Optional[str]=None
    recipient_document: Optional[str]=None
    transaction_date: datetime=datetime.today()

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "user_document": self.user_document,
            "value": self.value,
            "recipient_account_id": self.recipient_account_id,
            "recipient_document": self.recipient_document,
            "transaction_date": self.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        }
    

@dataclass
class AccountHistoryRequest:
    account_id: Optional[str]=None
    user_document: str=None
    start_date: Optional[datetime]=None
    end_date: Optional[datetime]=None

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "user_document": self.user_document,
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M:%S") if self.start_date else self.start_date,
            "end_date": self.end_date.strftime("%Y-%m-%d %H:%M:%S") if self.end_date else self.end_date
        } 
