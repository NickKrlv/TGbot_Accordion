from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class ButtonText:
    PROFILE = "👤 Профиль"
    CLOSE = "Закрыть"

def get_main_kb() -> ReplyKeyboardMarkup:
    """Основная клавиатура с кнопками Профиль и Закрыть"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonText.PROFILE)],
            [KeyboardButton(text=ButtonText.CLOSE)]
        ],
        resize_keyboard=True
    )
    return markup

def get_profile_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для профиля с кнопками регистрации и назад"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Зарегистрироваться")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    return markup

def get_cancel_kb() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    return markup