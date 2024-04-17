import pytest
from pymongo import MongoClient
from datetime import datetime, timedelta
from app.models.user import User
from app.models.account import Account
from app.api.services.user_service import UserService
from app.api.services.account_service import AccountService
from app.schemas.user_schemas import UserData
from app.schemas.account_schemas import *

from utils.static_vars import MONGODB_PATH
from app.database.mongodb import *


@pytest.fixture
def db():
    client = MongoClient(MONGODB_PATH)
    db = client.test_bank
    User.set_database(db)
    Account.set_database(db)
    yield db

    db.users.delete_many({})
    db.accounts.delete_many({})
    db.transactions_history.delete_many({})
    client.close()

@pytest.fixture
def default_user() -> User:
    user_data = UserData(
        "John", "Doe", "123456789", "123-456-789", "1999-01-01", "john@email.com"
    )

    return user_data


@pytest.fixture
def default_user_tmp() -> User:
    user_data = UserData(
        "Jane", "Doe", "987654321", "111-222-333", "1998-01-01", "jane@email.com"
    )

    return user_data
    

@pytest.fixture
def default_account() -> AccountData:
    return AccountData(
        user_document="123456789", balance=50
    )


@pytest.fixture
def default_account_tmp() -> AccountData:
    return AccountData(
        user_document="987654321", balance=100
    )


def test_service_create_account(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)


    service = AccountService(db).create_account(default_account)
    account = Account.find_by_document_id("123456789")

    assert account is not None


def test_service_delete_account(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    default_account.balance = 0
    service.create_account(default_account)

    service.delete_account(default_account)
    account = Account.find_by_document_id("123456789")

    assert account is None


def test_freeze_account(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)

    service.freeze_account(default_account)
    account = Account.find_by_document_id("123456789")

    assert account.is_frozen == True


def test_unfreeze_account(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)

    service.unfreeze_account(default_account)
    account = Account.find_by_document_id("123456789")

    assert account.is_frozen == False


def test_check_balance(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)

    balance = service.check_balance(default_account)

    assert balance == 50


def test_deposit(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)
    transaction_date = datetime.today()
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=50,
        transaction_date=transaction_date
    )

    service.deposit(transaction_data)
    account = Account.find_by_document_id("123456789")
    balance = service.check_balance(default_account)

    assert balance == 100
    assert account.last_date_transaction.strftime("%d-%m-%Y") == datetime.today().strftime("%d-%m-%Y")
    assert account.last_date_transactions_count == 1


def test_withdraw(db, default_user, default_account):
    user_data= default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)
    transaction_date = datetime.today()
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=30,
        transaction_date=transaction_date
    )

    service.withdraw(transaction_data)
    account = Account.find_by_document_id("123456789")
    balance = service.check_balance(default_account)

    assert balance == 20
    assert account.last_date_transaction.strftime("%d-%m-%Y") == datetime.today().strftime("%d-%m-%Y")
    assert account.last_date_transactions_count == 1


def test_transfer(db, default_user, default_account, default_user_tmp, default_account_tmp):
    user_data = default_user
    user_data_tmp = default_user_tmp
    UserService(db).create_user(user_data)
    UserService(db).create_user(user_data_tmp)
    service = AccountService(db)
    service.create_account(default_account)
    service.create_account(default_account_tmp)
    transaction_date = datetime.today()
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=30,
        recipient_document=user_data_tmp.document_id,
        transaction_date=transaction_date
    )

    service.transfer(transaction_data)
    account = Account.find_by_document_id("123456789")
    account_tmp = Account.find_by_document_id("987654321")
    balance = service.check_balance(default_account)
    balance_tmp = service.check_balance(default_account_tmp)

    assert balance == 20
    assert balance_tmp == 130
    assert account.last_date_transaction.strftime("%d-%m-%Y") == datetime.today().strftime("%d-%m-%Y")
    assert account.last_date_transactions_count == 1
    assert account_tmp.last_date_transactions_count == 0


def test_get_transactions_history_all_dates(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)
    transaction_date = datetime.today()
    
    service.deposit(AccountTransaction(
        user_document=user_data.document_id,
        value=50,
        transaction_date=transaction_date
    ))
    service.withdraw(AccountTransaction(
        user_document=user_data.document_id,
        value=100,
        transaction_date=transaction_date
    ))

    request_history = AccountHistoryRequest(
        user_document=user_data.document_id
    )

    transaction_history = service.get_transactions_history(request_history)

    assert len(transaction_history) == 2


def test_get_transactions_history_specific_range(db, default_user, default_account):
    user_data = default_user
    UserService(db).create_user(user_data)
    service = AccountService(db)
    service.create_account(default_account)
    transaction_date = datetime(2024, 1, 15)
    transaction_date_15daysbefore = datetime.today() - timedelta(days=15)
    service.deposit(AccountTransaction(
        user_document=user_data.document_id,
        value=50,
        transaction_date=transaction_date
    ))
    service.deposit(AccountTransaction(
        user_document=user_data.document_id,
        value=50,
        transaction_date=transaction_date_15daysbefore
    ))
    service.withdraw(AccountTransaction(
        user_document=user_data.document_id,
        value=100,
        transaction_date=datetime.today()
    ))

    request_history = AccountHistoryRequest(
        user_document=user_data.document_id,
        start_date=transaction_date_15daysbefore - timedelta(days=10),
        end_date=transaction_date_15daysbefore + timedelta(days=10) 
    )


    transaction_history = service.get_transactions_history(
        request_history
    )

    assert len(transaction_history) == 1


def test_get_transactions_history_recipient_user(db, default_user, default_user_tmp, default_account, default_account_tmp):
    user_data = default_user
    user_data_tmp = default_user_tmp
    UserService(db).create_user(user_data)
    UserService(db).create_user(user_data_tmp)
    service = AccountService(db)
    service.create_account(default_account)
    service.create_account(default_account_tmp)
    service.transfer(AccountTransaction(
        user_document=user_data.document_id,
        value=30,
        recipient_document=user_data_tmp.document_id,
        transaction_date=datetime.today()
    ))


    transactions_history = service.get_transactions_history(
        AccountHistoryRequest(user_document=user_data.document_id)
    )
    transactions_history_tmp = service.get_transactions_history(
        AccountHistoryRequest(user_document=user_data_tmp.document_id)
    )

    assert len(transactions_history) == 1
    assert len(transactions_history_tmp) == 1

