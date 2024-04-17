import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import APIRouter
from app.api.endpoints.users_endpoints import UserAPI
from app.api.endpoints.accounts_endpoints import AccountAPI

from app.models.user import User
from app.models.account import Account
from app.api.services.user_service import UserService
from app.api.services.account_service import AccountService
from app.schemas.user_schemas import *
from app.schemas.account_schemas import *
from utils.static_vars import MONGODB_PATH
from app.database.mongodb import *
from typing import List


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
def default_user():
    return {
        "firstname": "John",
        "lastname": "Doe",
        "document_id": "123456789",
        "birthdate": "1999-01-01",
        "phone": "123-456-789",
        "email": "john@email.com"
    }

@pytest.fixture
def default_user_tmp():
    return {
        "firstname": "Jane",
        "lastname": "Doe",
        "document_id": "987654321",
        "birthdate": "1998-01-01",
        "phone": "111-222-333",
        "email": "jane@email.com"
    }


@pytest.fixture
def default_account():
    return {
        "user_document": "123456789",
        "balance": 50
    }


@pytest.fixture
def default_account_tmp():
    return {
        "user_document": "987654321",
        "balance": 100
    }


@pytest.fixture
def app(db):
    application = FastAPI()
    user_router = APIRouter()
    account_router = APIRouter()

    # Setup User routes
    user_service = UserService(db)
    user_api = UserAPI(user_service)
    user_router.post("/create-user")(user_api.create_user)
    user_router.post("/update-user")(user_api.update_user)
    user_router.post("/delete-user")(user_api.delete_user)
    user_router.post("/info-user", response_model=dict)(user_api.get_user_info)

    # Setup Account routes
    account_service = AccountService(db)
    account_api = AccountAPI(account_service)
    account_router.post("/create-account")(account_api.create_account)
    account_router.post("/delete-account")(account_api.delete_account)
    account_router.post("/freeze-account")(account_api.freeze_account)
    account_router.post("/unfreeze-account")(account_api.unfreeze_account)
    account_router.post("/check-balance-account", response_model=dict)(account_api.check_balance)
    account_router.post("/deposit-account")(account_api.deposit)
    account_router.post("/withdraw-account")(account_api.withdraw)
    account_router.post("/transfer-account")(account_api.transfer)
    account_router.post("/get-transactions-history", response_model=List[dict])(account_api.get_transactions_history)

    # Include routers in the app
    application.include_router(user_router)
    application.include_router(account_router)

    return application

@pytest.fixture
def client(app):
    return TestClient(app)


def test_api_create_account(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)

    response = client.post("/create-account", json=account_data.to_dict())

    assert response.status_code == 200


def test_api_delete_account(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())

    print(account_data.to_dict())
    response = client.post("/delete-account", json=account_data.to_dict())

    assert response.status_code == 200


def test_api_freeze_account(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())

    response = client.post("/freeze-account", json=account_data.to_dict())

    assert response.status_code == 200


def test_api_unfreeze_account(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())

    response = client.post("/unfreeze-account", json=account_data.to_dict())

    assert response.status_code == 200


def test_api_check_balance_account(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())

    response = client.post("/check-balance-account", json=account_data.to_dict())

    assert response.status_code == 200


def test_api_deposit_account(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=50,
        transaction_date=datetime.today()
    )

    response = client.post("/deposit-account", json=transaction_data.to_dict())

    assert response.status_code == 200


def test_api_withdrawal(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=30,
        transaction_date=datetime.today()
    )

    response = client.post("/withdraw-account", json=transaction_data.to_dict())

    assert response.status_code == 200


def test_api_transfer(db, client, default_user, default_user_tmp, default_account, default_account_tmp):
    user_data = UserData(**default_user)
    user_data_tmp = UserData(**default_user_tmp)
    client.post("/create-user", json=user_data.to_dict())
    client.post("/create-user", json=user_data_tmp.to_dict())
    account_data = AccountData(**default_account)
    account_data_tmp = AccountData(**default_account_tmp)
    client.post("/create-account", json=account_data.to_dict())
    client.post("/create-account", json=account_data_tmp.to_dict())
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=30,
        recipient_document=user_data_tmp.document_id,
        transaction_date=datetime.today()
    )
    print(transaction_data.to_dict())

    response = client.post("/transfer-account", json=transaction_data.to_dict())
    print(response.json())

    assert response.status_code == 200


def test_api_get_transactions_history(db, client, default_user, default_account):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    account_data = AccountData(**default_account)
    client.post("/create-account", json=account_data.to_dict())
    transaction_data = AccountTransaction(
        user_document=user_data.document_id,
        value=50,
        transaction_date=datetime.today()
    )
    _ = client.post("/deposit-account", json=transaction_data.to_dict())
    request_history = AccountHistoryRequest(
        user_document=user_data.document_id
    )

    response = client.post("/get-transactions-history", json=request_history.to_dict())

    assert response.status_code == 200







