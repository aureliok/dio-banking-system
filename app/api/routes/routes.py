from fastapi import APIRouter, FastAPI
from app.models.user import User
from app.models.account import Account
from app.api.services.user_service import UserService
from app.api.services.account_service import AccountService
from app.api.endpoints.users_endpoints import UserAPI
from app.api.endpoints.accounts_endpoints import AccountAPI
from utils.static_vars import MONGODB_PATH
from pymongo import MongoClient

from typing import List

client = MongoClient(MONGODB_PATH)
db = client.bank
User.set_database(db)
Account.set_database(db)

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