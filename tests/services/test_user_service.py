import pytest
from pymongo import MongoClient
from app.models.user import User
from app.api.services.user_service import *
from app.schemas.user_schemas import UserData, UserUpdate

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
def default_user() -> User:
    return UserData(
        "John", "Doe", "123456789", "123-456-789", "1999-01-01", "john@email.com"
    )


def test_service_create_user(db, default_user):
    service = UserService(db)

    service.create_user(default_user)
    user = User.find_by_document("123456789")

    assert user is not None
    assert user.firstname == "John"
    assert user.lastname == "Doe"


def test_service_update_user_all_properties(db, default_user):
    service = UserService(db)
    service.create_user(default_user)

    update_data = UserUpdate("123456789", "11 1111 1111", "newemail@email.com")
    service.update_user(update_data)
    user = User.find_by_document("123456789")

    assert user.phone == "11 1111 1111"
    assert user.email == "newemail@email.com"


def test_service_update_user_partial_properties(db, default_user):
    service = UserService(db)
    service.create_user(default_user)

    update_data = UserUpdate("123456789", "11 1111 1111", None)
    service.update_user(update_data)
    user = User.find_by_document("123456789")

    assert user.phone == "11 1111 1111"
    assert user.email == "john@email.com"


def test_service_delete_user_valid_data(db, default_user):
    service = UserService(db)
    service.create_user(default_user)

    service.delete_user(default_user)
    user = User.find_by_document("123456789")

    assert user is None


def test_service_delete_user_invalid_data(db, default_user):
    service = UserService(db)
    user_data = service.create_user(default_user)
    default_user.firstname = None

    with pytest.raises(Exception):
        service.delete_user(default_user)

    
def test_service_get_user_info(db, default_user):
    service = UserService(db)
    user_data = service.create_user(default_user)

    user_info = service.get_user_info("123456789")

    assert user_info is not None
    assert user_info.firstname == "John"
    assert user_info.lastname == "Doe"
    assert user_info.phone == "123-456-789"
    assert user_info.birthdate == "1999-01-01"
    assert user_info.email == "john@email.com"