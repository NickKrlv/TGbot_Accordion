import sqlite3
import logging
from datetime import datetime
import atexit


class DatabaseManager:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name
        self.connection = None
        self.init_database()
        # Регистрируем функцию закрытия при выходе
        atexit.register(self.close_connection)

    def get_connection(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.info("Соединение с базой данных закрыто")

    def init_database(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Проверяем, существует ли таблица
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone()

            if not table_exists:
                # Создаем новую таблицу
                cursor.execute('''
                               CREATE TABLE users
                               (
                                   id                INTEGER PRIMARY KEY AUTOINCREMENT,
                                   telegram_id       INTEGER UNIQUE,
                                   username          TEXT,
                                   full_name         TEXT,
                                   birth_date        TEXT,
                                   registration_date TEXT,
                                   last_updated      TEXT,
                                   message_count     INTEGER DEFAULT 0
                               )
                               ''')
            else:
                # Проверяем, существует ли колонка message_count
                cursor.execute("PRAGMA table_info(users)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'message_count' not in columns:
                    # Добавляем колонку message_count
                    cursor.execute("ALTER TABLE users ADD COLUMN message_count INTEGER DEFAULT 0")

            conn.commit()
            logging.info("База данных инициализирована")
        except Exception as e:
            logging.error(f"Ошибка инициализации базы данных: {e}")

    def increment_message_count(self, telegram_id):
        """Увеличение счетчика сообщений пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                           UPDATE users
                           SET message_count = message_count + 1,
                               last_updated  = ?
                           WHERE telegram_id = ?
                           ''', (datetime.now().isoformat(), telegram_id))
            conn.commit()
            if cursor.rowcount > 0:
                logging.info(f"Счетчик сообщений увеличен для пользователя {telegram_id}")
                return True
            else:
                # Пользователь не найден в БД, создаем запись
                cursor.execute('''
                               INSERT
                               OR IGNORE INTO users 
                    (telegram_id, message_count, last_updated)
                    VALUES (?, 1, ?)
                               ''', (telegram_id, datetime.now().isoformat()))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Создана новая запись для пользователя {telegram_id} со счетчиком 1")
                    return True
            return False
        except Exception as e:
            logging.error(f"Ошибка увеличения счетчика сообщений для {telegram_id}: {e}")
            return False

    def get_user_message_count(self, telegram_id):
        """Получение счетчика сообщений пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT message_count FROM users WHERE telegram_id = ?', (telegram_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logging.error(f"Ошибка получения счетчика сообщений для {telegram_id}: {e}")
            return 0

    def get_inactive_users(self, min_messages=100):
        """Получение пользователей с количеством сообщений меньше заданного порога"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Получаем пользователей с message_count < min_messages
            cursor.execute('''
                           SELECT telegram_id, username, full_name, message_count
                           FROM users
                           WHERE message_count < ?
                             AND message_count >= 0
                           ORDER BY message_count ASC
                           ''', (min_messages,))

            users = cursor.fetchall()
            logging.info(f"Найдено {len(users)} неактивных пользователей")
            return users
        except Exception as e:
            logging.error(f"Ошибка при поиске неактивных пользователей: {e}")
            return []

    def reset_monthly_message_count(self):
        """Сброс ежемесячного счетчика сообщений"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Сбрасываем счетчик сообщений для всех пользователей
            cursor.execute('UPDATE users SET message_count = 0')
            conn.commit()

            count = cursor.rowcount
            logging.info(f"Сброшен счетчик сообщений для {count} пользователей")
            return count
        except Exception as e:
            logging.error(f"Ошибка сброса счетчика сообщений: {e}")
            return 0

    def get_user_message_count(self, telegram_id):
        """Получение счетчика сообщений пользователя"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT message_count FROM users WHERE telegram_id = ?', (telegram_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logging.error(f"Ошибка получения счетчика сообщений для {telegram_id}: {e}")
            return 0


# Создаем глобальный экземпляр
db_manager = DatabaseManager()