from fastapi import APIRouter
from app.api.endpoints.users_endpoints import UserAPI

router = APIRouter()
user_api = UserAPI()

router.post("/create-user")(user_api.create_user)
router.post("/update-user")(user_api.update_user)
router.post("/delete-user")(user_api.delete_user)
router.post("/info-user", response_model=dict)(user_api.delete_user)