import logging
from datetime import datetime, date
from aiogram import Router, types
from database.users_db import db_manager

router = Router(name=__name__)
logger = logging.getLogger(__name__)


def get_users_with_birthday_today():
    """Получение пользователей, у которых сегодня день рождения"""
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Получаем текущую дату
        today = date.today()
        today_str = today.strftime("%d.%m.%Y")
        day_month = today.strftime("%d.%m")  # Формат ДД.ММ

        # Ищем пользователей с совпадающей датой рождения (ДД.ММ)
        cursor.execute('''
                       SELECT telegram_id, full_name, birth_date
                       FROM users
                       WHERE substr(birth_date, 1, 5) = ?
                       ''', (day_month,))

        users = cursor.fetchall()
        logger.info(f"Найдено {len(users)} пользователей с днем рождения сегодня")
        return users
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователей с днем рождения: {e}")
        return []


async def send_birthday_congratulations(bot):
    """Отправка поздравлений пользователям с днем рождения"""
    try:
        users = get_users_with_birthday_today()

        if not users:
            logger.info("Сегодня нет дней рождения")
            return

        for user in users:
            telegram_id, full_name, birth_date = user

            # Вычисляем возраст
            try:
                birth_year = int(birth_date.split('.')[-1])
                current_year = datetime.now().year
                age = current_year - birth_year

                # Определяем правильное окончание для возраста
                if 11 <= age % 100 <= 14:
                    age_text = f"{age} летием"
                elif age % 10 == 1:
                    age_text = f"{age} летием"
                elif 2 <= age % 10 <= 4:
                    age_text = f"{age} летием"
                else:
                    age_text = f"{age} летием"
            except:
                age_text = "много летием"

            # Отправляем поздравление
            try:
                congratulation_message = (
                    f"🎉 Дорогой(ая) {full_name}!\n\n"
                    f"С Днём Рождения! 🎂\n"
                    f"Поздравляем тебя с {age_text}! 🎈\n\n"
                    f"Пусть этот день будет наполнен радостью, "
                    f"а весь год приносит тебе счастье и успех! 🌟"
                )

                await bot.send_message(
                    chat_id=-1001785421122,
                    text=congratulation_message
                )
                logger.info(f"Поздравление отправлено пользователю {full_name}")

            except Exception as e:
                logger.error(f"Ошибка отправки поздравления пользователю {telegram_id}: {e}")

    except Exception as e:
        logger.error(f"Ошибка в функции поздравлений: {e}")