from fastapi import APIRouter

from app.api.v1.intelligence_routes import router as intelligence_router

router = APIRouter()
router.include_router(intelligence_router, prefix="/intelligence")
