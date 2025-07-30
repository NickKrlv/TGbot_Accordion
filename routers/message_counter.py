import logging
from aiogram import Router, types
from database.users_db import db_manager

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(lambda message: message.chat.type in ["group", "supergroup"])
async def count_group_messages(message: types.Message):
    """Подсчет сообщений в группе"""
    # Игнорируем сообщения от бота самого себя
    if message.from_user.is_bot:
        return

    telegram_id = message.from_user.id
    username = message.from_user.username or "не указан"
    full_name = message.from_user.full_name

    logger.info(f"Сообщение от пользователя {telegram_id} ({username}) в группе {message.chat.id}")

    # Увеличиваем счетчик сообщений
    success = db_manager.increment_message_count(telegram_id)

    if not success:
        logger.warning(f"Не удалось обновить счетчик для пользователя {telegram_id}")