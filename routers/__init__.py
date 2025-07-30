__all__ = ("router",)
from aiogram import Router
from .base_commands import router as base_router
from .registration_handler import router as registration_router

router = Router(name=__name__)
router.include_routers(base_router, registration_router)