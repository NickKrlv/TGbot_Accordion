import logging
from aiogram import F, Router
from aiogram.filters import Command
from aiogram import types
from database.users_db import db_manager

router = Router(name=__name__)
logger = logging.getLogger(__name__)


# Тестовая команда для проверки поздравлений
@router.message(Command("test_birthday"), F.chat.type == "private")
async def test_birthday_command(message: types.Message, bot):
    """Тестовая команда для проверки поздравлений"""
    logger.info(f"Пользователь {message.from_user.id} запустил тест поздравлений")

    try:
        from routers.birthday_handler import send_birthday_congratulations
        await send_birthday_congratulations(bot)
        await message.answer("✅ Тест поздравлений завершен. Проверьте логи.")
    except Exception as e:
        logger.error(f"Ошибка теста поздравлений: {e}")
        await message.answer(f"❌ Ошибка теста: {e}")


# Команда для показа статистики пользователя
@router.message(Command("stats"), F.chat.type == "private")
async def show_user_stats(message: types.Message):
    """Показ статистики пользователя"""
    message_count = db_manager.get_user_message_count(message.from_user.id)
    await message.answer(f"📊 Вы отправили {message_count} сообщений в группах")


# Ручная проверка активности
@router.message(Command("activity_check"), F.chat.type == "private")
async def manual_activity_check(message: types.Message, bot):
    """Ручная проверка активности (только для администраторов)"""
    logger.info(f"Пользователь {message.from_user.id} запустил ручную проверку активности")

    try:
        from routers.activity_handler import check_monthly_activity
        # Укажите ID вашей группы здесь
        GROUP_CHAT_ID = -1001785421122  # Замените на ID вашей группы

        await message.answer("✅ Начинаем проверку активности...")
        await check_monthly_activity(bot, GROUP_CHAT_ID)
        await message.answer("✅ Проверка активности завершена!")

    except Exception as e:
        logger.error(f"Ошибка ручной проверки активности: {e}")
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("news_of_the_week"), F.chat.type == "private")
async def news_of_the_week(message: types.Message, bot):
    logger.info(f"Пользователь {message.from_user.id} запустил новости недели")

    text = (f"📰 Новости недели!\n\n"
            f"@Alphz58 снова полысел\n"
            f"На этом все")
    await bot.send_message(
        chat_id=-1001785421122,
        text=text,
        parse_mode="HTML"
    )