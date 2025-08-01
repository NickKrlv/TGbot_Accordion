import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from keyboards.main_kb import ButtonText, get_main_kb

router = Router(name=__name__)

# Только для групп
# @router.message(Command("start"), F.chat.type.in_({"group", "supergroup"}))
# async def cmd_start_group(message: types.Message):
#     logging.info(f"Пользователь {message.from_user.id} запустил бота в группе {message.chat.id}")
#     await message.answer(
#         "👋 Добро пожаловать!",
        # reply_markup=get_main_kb()
#   )

# Только для группы
@router.message(F.text == ButtonText.PROFILE, F.chat.type.in_({"group", "supergroup"}))
async def show_profile_group(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} нажал Профиль в группе")
    try:
        # Пробуем отправить сообщение в личку
        await message.from_user.send_message(
            "Переходим в личные сообщения...\n\n"
            "Здесь вы можете зарегистрироваться или посмотреть свой профиль.",
            reply_markup=get_main_kb()
        )
        await message.answer("✅ Проверьте личные сообщения от бота!")
    except Exception as e:
        logging.error(f"Ошибка отправки в личку: {e}")
        # Если пользователь не начал диалог с ботом
        bot_username = "Accordion_test_bot"
        await message.answer(
            "ℹ️ Для работы с профилем начните диалог со мной в личных сообщениях:\n"
            f"👉 @{bot_username}\n\n"
            "Затем нажмите кнопку '👤 Профиль' снова"
        )

# Только для группы
@router.message(F.text == ButtonText.CLOSE, F.chat.type.in_({"group", "supergroup"}))
async def close_keyboard_group(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} закрыл клавиатуру в группе")
    await message.answer(
        "Клавиатура скрыта. Чтобы открыть меню снова, отправьте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )