import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram.constants import PARSEMODE_MARKDOWN


def create_and_send_message(payload, telegram_token, chat_id):
    """Create and async send a message via bot."""
    bot = telegram.Bot(telegram_token)
    lesson = payload['new_attempts'][-1]['lesson_title']
    lesson_url = payload['new_attempts'][-1]['lesson_url']
    if payload['new_attempts'][-1]['is_negative']:
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
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    params = {}
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
            payload = response.json()
            if payload['status'] == 'timeout':
                timestamp = payload['timestamp_to_request']
                params = {
                    "timestamp": timestamp,
                }
            else:
                timestamp = payload['last_attempt_timestamp']
                params = {}
                create_and_send_message(
                    payload,
                    telegram_token,
                    chat_id
                )
        except requests.exceptions.ReadTimeout as err:
            logging.error(err)
        except requests.exceptions.ConnectionError as err:
            logging.error(err)
            time.sleep(5)


if __name__ == "__main__":
    main()
