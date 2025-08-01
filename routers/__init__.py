from aiogram import Router
from .base_commands import router as base_router
from .registration_handler import router as registration_router
from .echo_handlers import router as echo_router
from .tests import router as tests_router
from .activity_handler import router as activity_router

# Создаем главный роутер
router = Router(name=__name__)

# Включаем все роутеры
router.include_routers(
    base_router,
    registration_router,
    activity_router,
    tests_router,
    echo_router
)