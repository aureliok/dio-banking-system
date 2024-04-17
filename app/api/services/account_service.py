from app.models.account import Account
from app.schemas.account_schemas import AccountData, AccountTransaction, AccountHistoryRequest
from datetime import datetime
from decimal import Decimal


class AccountService:
    def __init__(self, db):
        self._db = db

    def create_account(self, account_data: AccountData):
        account = Account(**account_data.to_dict())
        account.create()
    

    def delete_account(self, account_data: AccountData):
        account = Account.find_by_document_id(account_data.user_document)
        if account:
            print('h')
            _ = account.delete()
    
    
    def freeze_account(self, account_data: AccountData):
        account = Account.find_by_document_id(account_data.user_document)
        if account:
            account.freeze()
    

    def unfreeze_account(self, account_data: AccountData):
        account = Account.find_by_document_id(account_data.user_document)
        if account:
            account.unfreeze()
    

    def check_balance(self, account_data: AccountData):
        account = Account.find_by_document_id(account_data.user_document)
        return account.balance_check()
    

    def deposit(self, account_data: AccountTransaction|dict):
        if isinstance(account_data, dict):
            account_data = AccountTransaction(**account_data)
            account_data.transaction_date = datetime.strptime(account_data.transaction_date, "%Y-%m-%d %H:%M:%S")

        account = Account.find_by_document_id(account_data.user_document)
        transaction_date = account_data.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        account.deposit(account_data.value)
        account.add_transaction(transaction_type="deposit", 
                                value=account_data.value, 
                                transaction_time=transaction_date)
        account.update_transaction_count(transaction_date)
    

    def withdraw(self, account_data: AccountTransaction|dict):
        if isinstance(account_data, dict):
            account_data = AccountTransaction(**account_data)
            account_data.transaction_date = datetime.strptime(account_data.transaction_date, "%Y-%m-%d %H:%M:%S")

        account = Account.find_by_document_id(account_data.user_document)
        transaction_date = account_data.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        account.withdraw(account_data.value)
        account.add_transaction(transaction_type="withdraw", 
                                value=account_data.value, 
                                transaction_time=transaction_date)
        account.update_transaction_count(transaction_date)
    

    def transfer(self, account_data: AccountTransaction):
        account = Account.find_by_document_id(account_data.user_document)
        recipient_account = Account.find_by_document_id(account_data.recipient_document)
        transaction_date = account_data.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        account.transfer(recipient_account.account_id, account_data.value)

        account.add_transaction(transaction_type="transfer-out", 
                                value=account_data.value, 
                                counterpart=recipient_account.user_document, 
                                transaction_time=transaction_date)
        account.update_transaction_count(transaction_date)

        recipient_account.add_transaction(transaction_type="transfer-in", 
                                          value=account_data.value, 
                                          counterpart=account.user_document, 
                                          transaction_time=transaction_date)
    

    def get_transactions_history(self, account_data: AccountHistoryRequest):
        account = Account.find_by_document_id(account_data.user_document)
        transactions = account.get_transaction_history()

        if not account_data.end_date:
            account_data.end_date = datetime.now()

        if account_data.start_date:
            transactions = [t for t in transactions if t["timestamp"] >= account_data.start_date and t["timestamp"] <= account_data.end_date]

        for transaction in transactions:
            transaction["timestamp"] = transaction["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return transactions

        

