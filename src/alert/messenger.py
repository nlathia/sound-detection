from datetime import datetime
from telegram import Bot
import requests
import tenacity
from tenacity import (
    stop_after_attempt,
    wait_exponential,
)
import os

from src.util.audio import convert_to_mp3
from src.util.vars import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_ID,
    TELEGRAM_INTERVAL_SECONDS,
    logger
)


class TelegramMessenger:

    def __init__(self):
        self.last_message = None
        self.bot = Bot(os.environ[TELEGRAM_BOT_TOKEN])

    def can_send_message(self, force_send=False):
        if force_send or self.last_message is None:
            logger.info(f"ℹ️  Sending message: force_send={force_send}, "
                        f"last_message_exists={self.last_message is not None}.")
            return True
        seconds_since_last_message = (datetime.now() - self.last_message).seconds
        logger.info(f"ℹ️  Last message sent {(seconds_since_last_message / 60):.2f} minutes ago.")
        return seconds_since_last_message >= TELEGRAM_INTERVAL_SECONDS

    def set_message_sent(self, force_send=False):
        if not force_send:
            self.last_message = datetime.now()

    @tenacity.retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def send_text_message(self, message, force_send=False):
        text_url = f"https://api.telegram.org/bot{os.environ[TELEGRAM_BOT_TOKEN]}" \
                   f"/sendMessage?chat_id={os.environ[TELEGRAM_ID]}" \
                   f"&parse_mode=Markdown&text={message}"
        response = requests.get(text_url)
        result = response.json()
        logger.info(f"🤖  Bot message sent: {bool(result['ok'])}")
        if response.status_code != 200:
            logger.info(f"❌  send_text_message() failed with status={response.status_code}")
        if bool(result["ok"]):
            self.set_message_sent(force_send)
            return True

        logger.exception(f"❌  Failed to send text message: {response}")
        raise Exception(f"❌  Failed to send text message: {response}")

    @tenacity.retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def send_audio_message(self, mp3_file_path):
        logger.info(f"🤖  Trying to upload audio in {mp3_file_path}...")
        self.bot.send_voice(
            chat_id=os.environ[TELEGRAM_ID],
            voice=open(mp3_file_path, "rb")
        )

    def send_alert(self, message, wav_file_path=None, force_send=False):
        can_send = self.can_send_message(force_send)
        if not can_send:
            logger.info(f"❌  Not sending message: can_send={can_send}; force_send={force_send}.")
            return
        try:
            self.send_text_message(message, force_send)
            if wav_file_path is not None:
                mp3_file_path = convert_to_mp3(wav_file_path)
                if os.path.exists(mp3_file_path):
                    self.send_audio_message(mp3_file_path)
                    logger.info(f"🗑  Removing: {mp3_file_path}")
                    os.remove(mp3_file_path)
        except Exception as e:
            logger.info(f"❌  Failed to send alert: {str(e)}")
            logger.exception(e)
