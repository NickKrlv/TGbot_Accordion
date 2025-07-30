import logging
from datetime import datetime
from aiogram import Router, types
from aiogram.filters import Command
from database.users_db import db_manager

router = Router(name=__name__)
logger = logging.getLogger(__name__)


async def check_monthly_activity(bot, chat_id, min_messages=100):
    """Проверка активности пользователей за месяц"""
    try:
        logger.info("Начинаем проверку ежемесячной активности пользователей")

        # Получаем неактивных пользователей
        inactive_users = db_manager.get_inactive_users(min_messages)

        if not inactive_users:
            # Все пользователи активны
            message = "🎉 Отличная работа, все пользователи проявили хорошую активность в этом месяце!"
            await bot.send_message(chat_id=chat_id, text=message)
            logger.info("Все пользователи активны")
            return

        # Формируем сообщение со списком неактивных пользователей
        message = "⚠️ Список неактивных пользователей (менее 100 сообщений за месяц):\n\n"

        for i, (telegram_id, username, full_name, message_count) in enumerate(inactive_users, 1):
            if username:
                user_mention = f"@{username}"
            else:
                user_mention = f"<a href='tg://user?id={telegram_id}'>{full_name}</a>"

            message += f"{i}. {user_mention} - {message_count} сообщений\n"

        message += f"\n📢 Вы чё тут блять посмотреть зашли!?"

        # Отправляем сообщение в группу
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="HTML"
        )

        logger.info(f"Отправлен список {len(inactive_users)} неактивных пользователей")

        # Сбрасываем счетчики сообщений
        reset_count = db_manager.reset_monthly_message_count()
        logger.info(f"Сброшены счетчики для {reset_count} пользователей")

    except Exception as e:
        logger.error(f"Ошибка при проверке активности: {e}")
