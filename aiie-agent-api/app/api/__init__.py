from fastapi import APIRouter
from app.api.auth.router import router as auth_router
from app.api.message.router import router as message_router
from app.api.auth_google.router import router as auth_google_router
from app.api.conversation.router import router as conversation_router
from app.api.storage.router import router as storage_router
from app.api.user.router import user_router
from app.api.result.result_router import result_router
from app.api.image.router import router as image_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(message_router)
router.include_router(auth_google_router)
router.include_router(conversation_router)
router.include_router(storage_router)
router.include_router(user_router)
router.include_router(result_router)
router.include_router(image_router)
