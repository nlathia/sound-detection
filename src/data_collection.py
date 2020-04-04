from src.alert.messenger import TelegramMessenger
from src.record.microphone import audio_files


def run(messenger: TelegramMessenger, timeout: int):
    """
    Records a bunch of non-silent samples for `timeout` minutes.
    All of the non-silent samples will be saved in data/live/.

    Notifies you when it is started, nearly finished, and finished.
    """
    messenger.send_alert("👀  Starting to collect recording samples.", force_send=True)
    for _ in audio_files(timeout, messenger):
        pass
    messenger.send_alert("✅  I've stopped recording samples.", force_send=True)
