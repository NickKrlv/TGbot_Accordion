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
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS users
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               telegram_id
                               INTEGER
                               UNIQUE,
                               username
                               TEXT,
                               full_name
                               TEXT,
                               birth_date
                               TEXT,
                               registration_date
                               TEXT,
                               last_updated
                               TEXT
                           )
                           ''')
            conn.commit()
            logging.info("База данных инициализирована")
        except Exception as e:
            logging.error(f"Ошибка инициализации базы данных: {e}")


# Создаем глобальный экземпляр
db_manager = DatabaseManager()