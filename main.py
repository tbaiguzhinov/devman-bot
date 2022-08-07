import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram.constants import PARSEMODE_MARKDOWN


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def create_and_send_message(bot, works_and_reviews, chat_id):
    """Create and send a message via bot."""
    lesson = works_and_reviews['new_attempts'][-1]['lesson_title']
    lesson_url = works_and_reviews['new_attempts'][-1]['lesson_url']
    if works_and_reviews['new_attempts'][-1]['is_negative']:
        result = "К сожалению, в работе нашлись ошибки."
    else:
        result = "Преподавателю всё понравилось, можно приступать к следующему уроку!"
    message = f"У вас проверили работу \"[{lesson}]({lesson_url})\"\n\n{result}"
    bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode=PARSEMODE_MARKDOWN
    )


def main():
    """Main function."""
    load_dotenv()
    devman_token = os.getenv("DEVMAN_TOKEN")
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    logger_bot_token = os.getenv('LOGGER_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    params = {}
    bot = telegram.Bot(telegram_token)
    logger_bot = telegram.Bot(logger_bot_token)

    logger = logging.getLogger('Logger')
    logger.addHandler(TelegramLogsHandler(logger_bot, chat_id))

    logger.warning("Бот запущен")
    while True:
        try:
            response = requests.get(
                "https://dvmn.org/api/long_polling/",
                headers={
                    "Authorization":
                    f"Token {devman_token}",
                },
                params=params,
            )
            response.raise_for_status()
            works_and_reviews = response.json()
            if works_and_reviews['status'] == 'timeout':
                timestamp = works_and_reviews['timestamp_to_request']
                params = {
                    "timestamp": timestamp,
                }
            else:
                timestamp = works_and_reviews['last_attempt_timestamp']
                params = {}
                create_and_send_message(
                    bot,
                    works_and_reviews,
                    chat_id
                )
        except requests.exceptions.ReadTimeout as err:
            logger.error("Бот упал с ошибкой")
            logger.error(err)
        except requests.exceptions.ConnectionError as err:
            logger.error("Бот упал с ошибкой")
            logger.error(err)
            time.sleep(5)
        except KeyboardInterrupt:
            raise
        except Exception as err:
            logger.error("Бот упал с ошибкой")
            logger.error(err)
            time.sleep(5)


if __name__ == "__main__":
    main()
