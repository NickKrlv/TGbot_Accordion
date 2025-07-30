from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class ButtonText:
    PROFILE = "👤 Профиль"
    CLOSE = "Закрыть"
    EDIT_PROFILE = "✏️ Изменить"
    BACK_TO_MAIN = "⬅️ Назад"
    CONFIRM = "✅ Подтвердить"

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
            [KeyboardButton(text=ButtonText.BACK_TO_MAIN)]
        ],
        resize_keyboard=True
    )
    return markup

def get_user_profile_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для зарегистрированного пользователя"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonText.EDIT_PROFILE)],
            [KeyboardButton(text=ButtonText.BACK_TO_MAIN)]
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

def get_confirm_edit_kb() -> ReplyKeyboardMarkup:
    """Клавиатура для подтверждения изменений"""
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Подтвердить")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    return markup