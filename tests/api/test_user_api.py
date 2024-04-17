import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import APIRouter
from app.api.endpoints.users_endpoints import UserAPI

from app.models.user import User
from app.api.services.user_service import UserService
from app.schemas.user_schemas import *
from utils.static_vars import MONGODB_PATH
from app.database.mongodb import *


@pytest.fixture
def db():
    client = MongoClient(MONGODB_PATH)
    db = client.test_bank
    User.set_database(db)
    yield db

    db.users.delete_many({})
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
def user_api(db):
    service = UserService(db)
    return UserAPI(service)


@pytest.fixture
def client(user_api):
    app = FastAPI()
    router = APIRouter()
    router.post("/create-user")(user_api.create_user)
    router.post("/update-user")(user_api.update_user)
    router.post("/delete-user")(user_api.delete_user)
    router.post("/info-user", response_model=dict)(user_api.get_user_info)
    app.include_router(router)
    return TestClient(app)


def test_api_create_user(db, client, default_user):
    user_data = UserData(**default_user)
    
    response = client.post("/create-user", json=user_data.to_dict())

    assert response.status_code == 200


def test_api_update_user(db, client, default_user):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())
    user_data.email = "newemail@email.com"
    user_data.phone = "11 1111 1111"

    response = client.post("/update-user", json=user_data.to_dict())

    assert response.status_code == 200


def test_api_delete_user(db, client, default_user):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())

    response = client.post("/delete-user", json=user_data.to_dict())

    assert response.status_code == 200


def test_api_get_user_info(db, client, default_user):
    user_data = UserData(**default_user)
    client.post("/create-user", json=user_data.to_dict())

    response = client.post("/info-user", json=user_data.to_dict())

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert all(key in response.json() for key in user_data.to_dict().keys())



