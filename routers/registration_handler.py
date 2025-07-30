import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from states.registration_states import RegistrationStates
from keyboards.main_kb import ButtonText, get_main_kb, get_profile_kb, get_cancel_kb
from database.users_db import db_manager

router = Router(name=__name__)


# Функции работы с БД
def get_user(telegram_id):
    """Получение информации о пользователе"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        logging.error(f"Ошибка получения пользователя: {e}")
        return None


def save_user_to_db(user_data):
    """Сохранение пользователя в БД"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        from datetime import datetime
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (telegram_id, username, full_name, birth_date, registration_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_data['telegram_id'],
            user_data['username'],
            user_data['full_name'],
            user_data['birth_date'],
            user_data.get('registration_date', datetime.now().isoformat()),
            datetime.now().isoformat()
        ))
        conn.commit()
        logging.info(f"Пользователь {user_data['telegram_id']} сохранен в БД")
        return True
    except Exception as e:
        logging.error(f"Ошибка сохранения пользователя: {e}")
        return False


# Только для лички
@router.message(Command("start"), F.chat.type == "private")
async def cmd_start_private(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} запустил бота в личке")
    await message.answer(
        "👋 Добро пожаловать в личные сообщения с ботом!\n\n"
        "Здесь вы можете зарегистрироваться или посмотреть свой профиль.",
        reply_markup=get_main_kb()
    )


# Только для лички
@router.message(F.text == ButtonText.PROFILE, F.chat.type == "private")
async def show_profile_private(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} нажал Профиль в личке")
    user = get_user(message.from_user.id)

    if user:
        # Если пользователь уже зарегистрирован - показываем его данные
        profile_text = (
            "👤 Ваш профиль:\n\n"
            f"🆔 Telegram ID: {user[1]}\n"
            f"👤 Username: @{user[2] or 'не указан'}\n"
            f"📛 Имя: {user[3]}\n"
            f"🎂 Дата рождения: {user[4]}\n"
            f"📅 Дата регистрации: {user[5][:10]}"
        )
        await message.answer(profile_text, reply_markup=get_main_kb())
    else:
        # Если не зарегистрирован - предлагаем зарегистрироваться
        await message.answer(
            "❌ Вы еще не зарегистрированы.\n"
            "Нажмите кнопку ниже, чтобы зарегистрироваться:",
            reply_markup=get_profile_kb()
        )


# Только для лички
@router.message(F.text == "📝 Зарегистрироваться", F.chat.type == "private")
async def start_registration(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} начал регистрацию в личке")

    # Проверяем, не зарегистрирован ли уже
    user = get_user(message.from_user.id)
    if user:
        await message.answer(
            "❌ Вы уже зарегистрированы!",
            reply_markup=get_main_kb()
        )
        return

    # Автоматически получаем ID и username
    user_info = (
        f"🆔 Ваш Telegram ID: {message.from_user.id}\n"
        f"👤 Username: @{message.from_user.username or 'не указан'}\n\n"
        f"Введите ваше имя:"
    )

    await message.answer(user_info, reply_markup=get_cancel_kb())
    await state.set_state(RegistrationStates.waiting_for_name)


# Только для лички
@router.message(F.text == "⬅️ Назад", F.chat.type == "private")
async def go_back_to_main(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} нажал Назад")
    await message.answer(
        "Возвращаемся в главное меню:",
        reply_markup=get_main_kb()
    )


# Только для лички
@router.message(F.text == "❌ Отмена", F.chat.type == "private")
async def cancel_registration(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} отменил регистрацию")
    await state.clear()
    await message.answer(
        "❌ Регистрация отменена.",
        reply_markup=get_main_kb()
    )


# Обработчики регистрации - только для лички
@router.message(StateFilter(RegistrationStates.waiting_for_name), F.chat.type == "private")
async def process_name(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} вводит имя: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_registration(message, state)
        return

    await state.update_data(name=message.text)
    await message.answer(
        "🎂 Введите вашу дату рождения в формате ДД.ММ.ГГГГ (например: 25.12.1990):",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(RegistrationStates.waiting_for_birthday)


@router.message(StateFilter(RegistrationStates.waiting_for_birthday), F.chat.type == "private")
async def process_birthday(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} вводит дату рождения: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_registration(message, state)
        return

    # Проверка формата даты
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
        await message.answer(
            "❌ Неверный формат даты.\n"
            "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например: 25.12.1990):",
            reply_markup=get_cancel_kb()
        )
        return

    # Проверка корректности даты
    try:
        day, month, year = map(int, message.text.split('.'))
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2024):
            raise ValueError
    except ValueError:
        await message.answer(
            "❌ Некорректная дата.\n"
            "Пожалуйста, введите существующую дату в формате ДД.ММ.ГГГГ:",
            reply_markup=get_cancel_kb()
        )
        return

    await state.update_data(birthday=message.text)

    # Получаем все данные
    user_data = await state.get_data()

    # Формируем подтверждение
    confirmation_text = (
        "📋 Проверьте введенные данные:\n\n"
        f"🆔 Telegram ID: {message.from_user.id}\n"
        f"👤 Username: @{message.from_user.username or 'не указан'}\n"
        f"📛 Имя: {user_data['name']}\n"
        f"🎂 Дата рождения: {user_data['birthday']}\n\n"
        "Все верно? Отправьте '+' для подтверждения или '-' для отмены."
    )

    await message.answer(confirmation_text, reply_markup=get_cancel_kb())
    await state.set_state(RegistrationStates.waiting_for_confirmation)


@router.message(StateFilter(RegistrationStates.waiting_for_confirmation), F.chat.type == "private")
async def process_confirmation(message: types.Message, state: FSMContext):
    logging.info(f"Пользователь {message.from_user.id} подтверждает регистрацию: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_registration(message, state)
        return

    if message.text == '+':
        # Получаем данные из состояния
        user_data = await state.get_data()

        # Сохраняем в базу данных
        save_data = {
            'telegram_id': message.from_user.id,
            'username': message.from_user.username,
            'full_name': user_data['name'],
            'birth_date': user_data['birthday'],
        }

        if save_user_to_db(save_data):
            await message.answer(
                "✅ Регистрация успешно завершена!\n"
                "Спасибо за регистрацию!",
                reply_markup=get_main_kb()
            )
            logging.info(f"Пользователь {message.from_user.id} успешно зарегистрирован")
        else:
            await message.answer(
                "❌ Произошла ошибка при сохранении данных.\n"
                "Попробуйте зарегистрироваться позже.",
                reply_markup=get_main_kb()
            )
    else:
        await message.answer(
            "❌ Регистрация отменена.",
            reply_markup=get_main_kb()
        )

    await state.clear()

@router.message(F.text == ButtonText.CLOSE, F.chat.type == "private")
async def close_keyboard_private(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} закрыл клавиатуру в личке")
    await message.answer(
        "Клавиатура скрыта. Чтобы открыть меню снова, отправьте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )