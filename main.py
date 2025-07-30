import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.users_db import db_manager
from routers import router
from utils.birthday_scheduler import BirthdayScheduler
from utils.activity_scheduler import ActivityScheduler


# Настраиваем логирование
def setup_logging():
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    return root_logger


logger = setup_logging()
logger.info("=== ЗАПУСК БОТА ===")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Подключаем роутеры
dp.include_router(router)

# Создаем планировщики
birthday_scheduler = BirthdayScheduler(bot)
# Укажите ID вашей группы здесь
GROUP_CHAT_ID = -1001785421122  # Замените на ID вашей группы
activity_scheduler = ActivityScheduler(bot, GROUP_CHAT_ID)


async def main():
    logger.info("Бот запущен и ожидает сообщений...")
    try:
        # Запускаем планировщики
        birthday_scheduler.start_scheduler()
        activity_scheduler.start_scheduler()

        # Запускаем бота
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Ошибка запуска: {e}", exc_info=True)
    finally:
        logger.info("Бот остановлен")
        # Останавливаем планировщики
        birthday_scheduler.stop_scheduler()
        activity_scheduler.stop_scheduler()
        await bot.session.close()
        db_manager.close_connection()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)