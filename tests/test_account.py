import pytest
from pymongo import MongoClient
from app.models.account import Account
from app.models.user import User

from utils.static_vars import MONGODB_PATH
from app.database.mongodb import *


@pytest.fixture
def db():
    client = MongoClient(MONGODB_PATH)
    db = client.test_bank
    create_accounts_indexes(db)
    create_users_indexes(db)
    User.set_database(db)
    Account.set_database(db)
    yield db

    db.users.delete_many({})
    client.close()

@pytest.fixture
def default_account() -> Account:
    return Account(
        "123456789", 50, False 
    )

@pytest.fixture
def default_user() -> User:
    return User(
        "John", "Doe", "123456789", "123-456-789", "1999-01-01", "john@email.com"
    )


def test_create_account_with_valid_user(db, default_account, default_user):
    _ = default_user.create()
    _ = User.find_by_document("123456789")

    account_id = default_account.create()

    assert account_id is not None


def test_create_account_with_novalid_user(db, default_account):
    with pytest.raises(Exception):
        default_account.create()


def test_delete_account_with_nobalance(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()
    
    account.withdraw(50)
    delete_count = account.delete()

    assert delete_count == 1   


def test_delete_account_with_balance(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()
    
    delete_count = account.delete()

    assert delete_count == 0    


def test_freeze_account(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()

    account.freeze()
    updated_account = Account.find_by_account_id(account.account_id)
    
    assert updated_account["is_frozen"] == True


def test_unfreeze_account(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()

    account.unfreeze()
    updated_account = Account.find_by_account_id(account.account_id)
    
    assert updated_account["is_frozen"] == False


def test_balance_check(db, default_account, default_user):
    default_user.create()
    default_account.create()
    account_data = Account.find_by_document_id("123456789")
    del account_data["_id"]
    del account_data["accounts"]
    print(account_data)
    account = Account(**account_data)

    balance = account.balance_check()

    assert balance == 50


def test_deposit(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()

    account.deposit(50)
    updated_account = Account.find_by_account_id(account.account_id)

    assert updated_account["balance"] == 100


def test_withdraw_with_balance(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()

    account.withdraw(20.5)
    updated_account = Account.find_by_account_id(account.account_id)

    assert updated_account["balance"] == 29.5


def test_withdraw_with_nobalance(db, default_account, default_user):
    _ = default_user.create()
    account = default_account
    account.create()

    account.withdraw(70)
    updated_account = Account.find_by_account_id(account.account_id)

    assert updated_account["balance"] == 50


def test_transfer_with_balance(db, default_account, default_user):
    user1 = default_user
    account1 = default_account
    user1.create()
    account1.create()
    user2 = User("Jane", "Doe", "987654321", "111-456-789", "2000-01-01", "jane@email.com")
    account2 = Account("987654321", 60, False)
    user2.create()
    account2.create()

    account1.transfer(account2.account_id, 30)
    updated_account1 = Account.find_by_account_id(account1.account_id)
    updated_account2 = Account.find_by_account_id(account2.account_id)

    assert updated_account1["balance"] == 20
    assert updated_account2["balance"] == 90


def test_transfer_with_nobalance(db, default_account, default_user):
    user1 = default_user
    account1 = default_account
    user1.create()
    account1.create()
    user2 = User("Jane", "Doe", "987654321", "111-456-789", "2000-01-01", "jane@email.com")
    account2 = Account("987654321", 60, False)
    user2.create()
    account2.create()

    account1.transfer(account2.account_id, 60)
    updated_account1 = Account.find_by_account_id(account1.account_id)
    updated_account2 = Account.find_by_account_id(account2.account_id)

    assert updated_account1["balance"] == 50
    assert updated_account2["balance"] == 60


def test_find_by_document_id_account_exists(db, default_account, default_user):
    _ = default_user.create()
    _ = default_account.create()

    account = Account.find_by_document_id("123456789")

    assert account is not None


def test_find_by_document_id_account_doesnt_exist(db):
    account = Account.find_by_document_id("12345678")

    assert account is None


def test_find_by_account_id_account_exists(db, default_account, default_user):
    _ = default_user.create()
    _ = default_account.create()

    account = Account.find_by_account_id(default_account.account_id)

    assert account is not None


def test_find_by_account_id_account_doesnt_exist(db):
    account = Account.find_by_account_id("15431051478")

    assert account is None


def test_add_transaction(self):
    raise NotImplementedError()


def test_get_transaction_history(self):
    raise NotImplementedError()
