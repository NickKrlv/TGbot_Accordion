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


# Настраиваем логирование ПРАВИЛЬНО - до всего остального
def setup_logging():
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Очищаем существующие обработчики
    root_logger.handlers.clear()

    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # Файловый обработчик
    file_handler = logging.FileHandler('bot.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    return root_logger


# Настраиваем логирование ДО ВСЕГО
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


async def main():
    logger.info("Бот запущен и ожидает сообщений...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}", exc_info=True)
    finally:
        logger.info("Бот остановлен")
        await bot.session.close()
        # Закрываем соединение с базой данных
        db_manager.close_connection()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)