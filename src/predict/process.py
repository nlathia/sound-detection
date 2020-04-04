from torch.nn.functional import softmax
import multiprocessing
import time
import os

from src.predict.model import (
    load_model,
    load_labels
)
from src.alert.messenger import TelegramMessenger
from src.util.audio import load_audio
from src.util.vars import logger


class RecordingClassifierProcess(multiprocessing.Process):

    def __init__(self, task_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.model = load_model()
        self.labels = load_labels()
        self.alerts = TelegramMessenger()

    def predict(self, file_path):
        audio = load_audio(file_path)
        output = self.model(audio)
        predicted_class = int(output.argmax(1))

        label = bool(self.labels[predicted_class])
        predicted_probability = float(softmax(output, dim=1).squeeze()[1])

        logger.info(f"🏷  Beep detected? {label}, {(predicted_probability * 100):.2f}% probability.")
        return label, predicted_probability

    def run(self):
        try:
            logger.info(f"⏩  Starting process: {self.name}...")
            while True:
                wav_file_path = self.task_queue.get()
                logger.info(f"ℹ️  Next task is: {wav_file_path}")
                if wav_file_path == "stop":
                    logger.info(f"🛑 Stopping: {self.name} from poison pill.")
                    self.task_queue.task_done()
                    break

                beep_detected, predicted_probability = self.predict(wav_file_path)
                if beep_detected:
                    message = f"🚨  Beep detected with {(predicted_probability * 100):.2f}% probability."
                    self.alerts.send_alert(message, wav_file_path)

                logger.info(f"🗑  Removing {wav_file_path}.")
                os.remove(wav_file_path)
                self.task_queue.task_done()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping: {self.name} from keyboard interrupt.")
        except Exception as e:
            logger.info(f"🛑 Stopping: {self.name} from exception: {str(e)}")
            logger.exception(e)
        logger.info(f"✅  classifier process finished.")
