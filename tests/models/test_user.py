import pytest
from pymongo import MongoClient
from app.models.user import User

from utils.static_vars import MONGODB_PATH


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
    return User(
        "John", "Doe", "123456789", "123-456-789", "1999-01-01", "john@email.com"
    )


def test_create_user(db, default_user):
    user_id = default_user.create()

    assert user_id is not None


def test_update_user_all_properties(db, default_user):
    user_id = default_user.create()
    data = {
        "phone": "99 8888 7777",
        "email": "changedemail@email.com"
    }

    default_user.update(data)
    changed_user = User.find_by_document("123456789")

    assert changed_user.phone == "99 8888 7777"
    assert changed_user.email == "changedemail@email.com"


def test_update_user_partial_properties(db, default_user):
    user_id = default_user.create()
    data = {
        "phone": "99 8888 7777",
    }

    default_user.update(data)
    changed_user = User.find_by_document("123456789")

    assert changed_user.phone == "99 8888 7777"
    assert changed_user.email == "john@email.com"
    


def test_delete_user(db, default_user):
    user = default_user
    _ = user.create()
    delete_result = user.delete()

    assert delete_result.deleted_count == 1


def test_find_by_name_user_exists(db, default_user):
    _ = default_user.create()
    found_user = User.find_by_name("John", "Doe")

    assert found_user is not None
    assert found_user.document_id == "123456789"
    assert found_user.firstname == "John"
    assert found_user.lastname == "Doe"


def test_find_by_name_user_doesnt_exist(db):
    found_user = User.find_by_name("John", "Doe")

    assert found_user is None


def test_find_by_document_user_exists(db, default_user):
    _ = default_user.create()
    found_user = User.find_by_document("123456789")

    assert found_user is not None
    assert found_user.document_id == "123456789"
    assert found_user.firstname == "John"
    assert found_user.lastname == "Doe"


def test_find_by_document_user_doesnt_exist(db):
    found_user = User.find_by_document("123456789")

    assert found_user is None