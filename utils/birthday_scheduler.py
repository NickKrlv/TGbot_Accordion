import asyncio
import logging
from datetime import datetime, timedelta
import threading
from routers.birthday_handler import send_birthday_congratulations

logger = logging.getLogger(__name__)


class BirthdayScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.is_running = False
        self.thread = None
        self.last_check_date = None  # Для отслеживания последней проверки

    def start_scheduler(self):
        """Запуск планировщика поздравлений"""
        if self.is_running:
            logger.info("Планировщик уже запущен")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Планировщик поздравлений запущен")

    def stop_scheduler(self):
        """Остановка планировщика"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Планировщик поздравлений остановлен")

    def _run_scheduler(self):
        """Основной цикл планировщика"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.is_running:
            try:
                # Проверяем, нужно ли отправлять поздравления (в 15:24 для теста)
                now = datetime.now()
                if now.hour == 8 and now.minute == 00:
                    # Проверяем, не отправляли ли мы уже сегодня
                    today_str = now.strftime("%Y-%m-%d")
                    if self.last_check_date != today_str:
                        logger.info("Начинаем проверку дней рождения...")
                        self.last_check_date = today_str

                        # Отправляем поздравления
                        future = asyncio.run_coroutine_threadsafe(
                            send_birthday_congratulations(self.bot),
                            loop
                        )
                        # Ждем завершения (максимум 30 секунд)
                        try:
                            future.result(timeout=30)
                        except Exception as e:
                            logger.error(f"Ошибка при отправке поздравлений: {e}")

                        logger.info("Проверка дней рождения завершена")

                # Ждем 59 секунд перед следующей проверкой
                # (чтобы точно не пропустить минуту)
                asyncio.run_coroutine_threadsafe(
                    asyncio.sleep(59),
                    loop
                ).result()

            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                try:
                    asyncio.run_coroutine_threadsafe(
                        asyncio.sleep(60),
                        loop
                    ).result()
                except:
                    pass