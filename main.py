import requests
import logging
import time
import asyncio
import telegram
import os
from telegram.constants import ParseMode
from dotenv import load_dotenv

async def main():
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token)
    params = {}
    while True:
        try:
            response = requests.get(
                "https://dvmn.org/api/long_polling/",
                headers={
                    "Authorization": 
                    "Token 6a79fdc07fad82953774f6451b7e5dabfbccf478",
                },
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            if data['status'] == 'timeout':
                timestamp = data['timestamp_to_request']
                params = {
                    "timestamp": timestamp,
                }
            else:
                timestamp = data['last_attempt_timestamp']
                params = {}
                lesson = data['new_attempts'][-1]['lesson_title']
                lesson_url = data['new_attempts'][-1]['lesson_url']
                if data['new_attempts'][-1]['is_negative']:
                    result = "К сожалению, в работе нашлись ошибки."
                else:
                    result = "Преподавателю всё понравилось, можно приступать к следующему уроку!"
                message = f"У вас проверили работу \"[{lesson}]({lesson_url})\"\n\n{result}"
                async with bot:
                    await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        except requests.exceptions.ReadTimeout as err:
            logging.error(err)
        except requests.exceptions.ConnectionError as err:
            logging.error(err)
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
