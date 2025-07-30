import logging
import re
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from states.registration_states import RegistrationStates, EditProfileStates
from keyboards.main_kb import (
    ButtonText, get_main_kb, get_profile_kb, get_cancel_kb,
    get_user_profile_kb, get_confirm_edit_kb
)
from database.users_db import db_manager

router = Router(name=__name__)
logger = logging.getLogger(__name__)


# Функции работы с БД с логированием
def get_user(telegram_id):
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        logger.info(f"Получен пользователь {telegram_id}: {'найден' if user else 'не найден'}")
        return user
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {telegram_id}: {e}")
        return None


def save_user_to_db(user_data):
    """Сохранение пользователя в БД"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        from datetime import datetime

        current_time = datetime.now().isoformat()

        # Проверяем, существует ли уже пользователь
        cursor.execute('SELECT registration_date FROM users WHERE telegram_id = ?',
                       (user_data['telegram_id'],))
        existing_user = cursor.fetchone()

        if existing_user:
            # Если пользователь уже существует, сохраняем дату регистрации
            registration_date = existing_user[0]
            # Обновляем только last_updated
            cursor.execute('''
                           UPDATE users
                           SET username     = ?,
                               full_name    = ?,
                               birth_date   = ?,
                               last_updated = ?
                           WHERE telegram_id = ?
                           ''', (
                               user_data['username'],
                               user_data['full_name'],
                               user_data['birth_date'],
                               current_time,
                               user_data['telegram_id']
                           ))
        else:
            # Если новый пользователь, устанавливаем обе даты
            cursor.execute('''
                           INSERT INTO users
                           (telegram_id, username, full_name, birth_date, registration_date, last_updated)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', (
                               user_data['telegram_id'],
                               user_data['username'],
                               user_data['full_name'],
                               user_data['birth_date'],
                               current_time,
                               current_time
                           ))

        conn.commit()
        logging.info(f"Пользователь {user_data['telegram_id']} {'обновлен' if existing_user else 'сохранен'} в БД")
        return True
    except Exception as e:
        logging.error(f"Ошибка сохранения пользователя {user_data['telegram_id']}: {e}")
        return False


@router.message(Command("start"), F.chat.type == "private")
async def cmd_start_private(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота в личке")
    await message.answer(
        "👋 Добро пожаловать в личные сообщения с ботом!\n\n"
        "Здесь вы можете зарегистрироваться или посмотреть свой профиль.",
        reply_markup=get_main_kb()
    )


@router.message(F.text == ButtonText.PROFILE, F.chat.type == "private")
async def show_profile_private(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} нажал Профиль в личке")
    user = get_user(message.from_user.id)

    if user:
        # Получаем счетчик сообщений
        message_count = db_manager.get_user_message_count(message.from_user.id)

        # Если пользователь уже зарегистрирован - показываем его данные с кнопкой Изменить
        # Добавляем проверки на None для каждого поля
        telegram_id = user[1] if len(user) > 1 and user[1] else "Не указан"
        username = user[2] if len(user) > 2 and user[2] else "не указан"
        full_name = user[3] if len(user) > 3 and user[3] else "Не указан"
        birth_date = user[4] if len(user) > 4 and user[4] else "Не указана"
        registration_date = user[5][:10] if len(user) > 5 and user[5] else "Не указана"
        last_updated = user[6][:10] if len(user) > 6 and user[6] else "Не указана"

        profile_text = (
            "👤 Ваш профиль:\n\n"
            f"🆔 Telegram ID: {telegram_id}\n"
            f"👤 Username: @{username}\n"
            f"📛 Имя: {full_name}\n"
            f"🎂 Дата рождения: {birth_date}\n"
            f"📊 Сообщений в группах: {message_count}\n"
            f"📅 Дата регистрации: {registration_date}\n"
            f"🔄 Последнее обновление: {last_updated}"
        )
        await message.answer(profile_text, reply_markup=get_user_profile_kb())
        logger.info(f"Профиль пользователя {message.from_user.id} отправлен (сообщений: {message_count})")
    else:
        # Если не зарегистрирован - предлагаем зарегистрироваться
        await message.answer(
            "❌ Вы еще не зарегистрированы.\n"
            "Нажмите кнопку ниже, чтобы зарегистрироваться:",
            reply_markup=get_profile_kb()
        )
        logger.info(f"Пользователь {message.from_user.id} не зарегистирован")


@router.message(F.text == ButtonText.EDIT_PROFILE, F.chat.type == "private")
async def start_edit_profile(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал редактирование профиля")

    user = get_user(message.from_user.id)
    if not user:
        await message.answer(
            "❌ Вы еще не зарегистрированы!\n"
            "Сначала зарегистрируйтесь.",
            reply_markup=get_main_kb()
        )
        return

    # Автоматически получаем текущие данные пользователя
    current_name = user[3] if user[3] else ""
    current_birthday = user[4] if user[4] else ""

    # Сохраняем текущие данные в состояние
    await state.update_data(
        current_name=current_name,
        current_birthday=current_birthday
    )

    # Предлагаем ввести новое имя
    await message.answer(
        f"📝 Текущее имя: {current_name}\n"
        f"Введите новое имя (или отправьте '-' чтобы оставить текущее):",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(EditProfileStates.waiting_for_name)


@router.message(F.text == ButtonText.CLOSE, F.chat.type == "private")
async def close_keyboard_private(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} закрыл клавиатуру в личке")
    await message.answer(
        "Клавиатура скрыта. Чтобы открыть меню снова, отправьте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(F.text == ButtonText.BACK_TO_MAIN, F.chat.type == "private")
async def go_back_to_main(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} вернулся в главное меню")
    await message.answer(
        "Возвращаемся в главное меню:",
        reply_markup=get_main_kb()
    )


@router.message(F.text == "📝 Зарегистрироваться", F.chat.type == "private")
async def start_registration(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал регистрацию в личке")

    user = get_user(message.from_user.id)
    if user:
        await message.answer(
            "❌ Вы уже зарегистрированы!\n"
            "Вы можете посмотреть или изменить свой профиль.",
            reply_markup=get_main_kb()
        )
        logger.info(f"Пользователь {message.from_user.id} уже зарегистирован")
        return

    # Автоматически получаем ID и username
    user_info = (
        f"🆔 Ваш Telegram ID: {message.from_user.id}\n"
        f"👤 Username: @{message.from_user.username or 'не указан'}\n\n"
        f"Введите ваше имя:"
    )

    await message.answer(user_info, reply_markup=get_cancel_kb())
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(F.text == "❌ Отмена", F.chat.type == "private")
async def cancel_operation(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} отменил операцию")
    await state.clear()
    await message.answer(
        "❌ Операция отменена.",
        reply_markup=get_main_kb()
    )


# Обработчики регистрации
@router.message(StateFilter(RegistrationStates.waiting_for_name), F.chat.type == "private")
async def process_name(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вводит имя: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_operation(message, state)
        return

    await state.update_data(name=message.text)
    await message.answer(
        "🎂 Введите вашу дату рождения в формате ДД.ММ.ГГГГ (например: 25.12.1990):",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(RegistrationStates.waiting_for_birthday)


@router.message(StateFilter(RegistrationStates.waiting_for_birthday), F.chat.type == "private")
async def process_birthday(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вводит дату рождения: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_operation(message, state)
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
        "Все верно? Нажмите кнопку подтверждения ниже:"
    )

    await message.answer(confirmation_text, reply_markup=get_confirm_edit_kb())
    await state.set_state(RegistrationStates.waiting_for_confirmation)


@router.message(StateFilter(RegistrationStates.waiting_for_confirmation), F.chat.type == "private")
async def process_registration_confirmation(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} подтверждает регистрацию: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_operation(message, state)
        return

    if message.text == "✅ Подтвердить":
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
            logger.info(f"Пользователь {message.from_user.id} успешно зарегистрирован")
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


# Обработчики редактирования профиля
@router.message(StateFilter(EditProfileStates.waiting_for_name), F.chat.type == "private")
async def process_edit_name(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вводит новое имя: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_operation(message, state)
        return

    # Если пользователь отправил "-", оставляем текущее имя
    if message.text == '-':
        user_data = await state.get_data()
        new_name = user_data.get('current_name', '')
    else:
        new_name = message.text

    await state.update_data(new_name=new_name)
    await message.answer(
        "🎂 Введите новую дату рождения в формате ДД.ММ.ГГГГ (например: 25.12.1990)\n"
        "или отправьте '-' чтобы оставить текущую:",
        reply_markup=get_cancel_kb()
    )
    await state.set_state(EditProfileStates.waiting_for_birthday)


@router.message(StateFilter(EditProfileStates.waiting_for_birthday), F.chat.type == "private")
async def process_edit_birthday(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} вводит новую дату рождения: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_operation(message, state)
        return

    # Если пользователь отправил "-", оставляем текущую дату рождения
    if message.text == '-':
        user_data = await state.get_data()
        new_birthday = user_data.get('current_birthday', '')
    else:
        # Проверка формата даты
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', message.text):
            await message.answer(
                "❌ Неверный формат даты.\n"
                "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ (например: 25.12.1990)\n"
                "или отправьте '-' чтобы оставить текущую:",
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
                "Пожалуйста, введите существующую дату в формате ДД.ММ.ГГГГ\n"
                "или отправьте '-' чтобы оставить текущую:",
                reply_markup=get_cancel_kb()
            )
            return

        new_birthday = message.text

    await state.update_data(new_birthday=new_birthday)

    # Получаем все данные
    user_data = await state.get_data()

    # Формируем подтверждение
    confirmation_text = (
        "📋 Проверьте новые данные:\n\n"
        f"🆔 Telegram ID: {message.from_user.id}\n"
        f"👤 Username: @{message.from_user.username or 'не указан'}\n"
        f"📛 Имя: {user_data['new_name']}\n"
        f"🎂 Дата рождения: {user_data['new_birthday']}\n\n"
        "Все верно? Нажмите '✅ Подтвердить' для сохранения или '❌ Отмена' для отмены."
    )

    await message.answer(confirmation_text, reply_markup=get_confirm_edit_kb())
    await state.set_state(EditProfileStates.waiting_for_confirmation)


@router.message(StateFilter(EditProfileStates.waiting_for_confirmation), F.chat.type == "private")
async def process_edit_confirmation(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} подтверждает изменения: {message.text}")

    if message.text == "❌ Отмена":
        await cancel_operation(message, state)
        return

    if message.text == "✅ Подтвердить":
        # Получаем данные из состояния
        user_data = await state.get_data()

        # Сохраняем в базу данных
        save_data = {
            'telegram_id': message.from_user.id,
            'username': message.from_user.username,
            'full_name': user_data['new_name'],
            'birth_date': user_data['new_birthday'],
        }

        if save_user_to_db(save_data):
            await message.answer(
                "✅ Профиль успешно обновлен!",
                reply_markup=get_main_kb()
            )
            logger.info(f"Профиль пользователя {message.from_user.id} успешно обновлен")
        else:
            await message.answer(
                "❌ Произошла ошибка при сохранении данных.\n"
                "Попробуйте позже.",
                reply_markup=get_main_kb()
            )
    else:
        await message.answer(
            "❌ Изменения отменены.",
            reply_markup=get_main_kb()
        )

    await state.clear()


