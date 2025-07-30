from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ButtonText:
    REGISTER = "📝 Зарегистрироваться"
    CANCEL = "❌ Отмена"
    PROFILE = "👤 Мой профиль"
    CLOSE = "Закрыть"

def get_main_kb() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonText.REGISTER)],
            [KeyboardButton(text=ButtonText.PROFILE)],
            [KeyboardButton(text=ButtonText.CLOSE)]
        ],
        resize_keyboard=True
    )
    return markup

def get_cancel_kb() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonText.CANCEL)]
        ],
        resize_keyboard=True
    )
    return markup