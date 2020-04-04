import multiprocessing

from src.predict.process import RecordingClassifierProcess
from src.record.microphone import audio_files
from src.alert.messenger import TelegramMessenger
from src.util.vars import logger


def run(messenger: TelegramMessenger, timeout: int):
    """
    Records a bunch of non-silent samples for `timeout` minutes.
    Each non-silent sample file is passed to the classifier process.

    Notifies you when it is started, nearly finished, and finished.
    """
    messenger.send_alert("👀  Starting to monitor for beeps.", force_send=True)

    task_queue = multiprocessing.JoinableQueue()
    classifier_process = RecordingClassifierProcess(task_queue)
    classifier_process.start()

    for file_path in audio_files(timeout, messenger):
        if not classifier_process.is_alive():
            logger.info(f"🛑  Classifier has died. Stopping...")
            messenger.send_alert(f"🤖 The classifier process has died!", force_send=True)
            break
        task_queue.put(file_path)

    task_queue.put("stop")
    classifier_process.join()

    messenger.send_alert("✅  I've stopped monitoring for beeps.", force_send=True)
