import asyncio
import logging
from datetime import datetime
import threading
from routers.activity_handler import check_monthly_activity

logger = logging.getLogger(__name__)


class ActivityScheduler:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id  # ID группы для отправки сообщений
        self.is_running = False
        self.thread = None
        self.last_check_date = None

    def start_scheduler(self):
        """Запуск планировщика проверки активности"""
        if self.is_running:
            logger.info("Планировщик активности уже запущен")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Планировщик проверки активности запущен")

    def stop_scheduler(self):
        """Остановка планировщика"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Планировщик проверки активности остановлен")

    def _run_scheduler(self):
        """Основной цикл планировщика"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.is_running:
            try:
                # Проверяем, нужно ли отправлять проверку активности (30 числа в 10:00)
                now = datetime.now()
                if now.day == 30 and now.hour == 10 and now.minute == 0:
                    # Проверяем, не отправляли ли мы уже сегодня
                    today_str = now.strftime("%Y-%m-%d")
                    if self.last_check_date != today_str:
                        logger.info("Начинаем ежемесячную проверку активности...")
                        self.last_check_date = today_str

                        # Отправляем проверку активности
                        future = asyncio.run_coroutine_threadsafe(
                            check_monthly_activity(self.bot, self.chat_id),
                            loop
                        )
                        # Ждем завершения (максимум 30 секунд)
                        try:
                            future.result(timeout=30)
                        except Exception as e:
                            logger.error(f"Ошибка при проверке активности: {e}")

                        logger.info("Ежемесячная проверка активности завершена")

                # Ждем 59 секунд перед следующей проверкой
                asyncio.run_coroutine_threadsafe(
                    asyncio.sleep(59),
                    loop
                ).result()

            except Exception as e:
                logger.error(f"Ошибка в планировщике активности: {e}")
                try:
                    asyncio.run_coroutine_threadsafe(
                        asyncio.sleep(60),
                        loop
                    ).result()
                except:
                    pass