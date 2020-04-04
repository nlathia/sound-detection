import os
import torch

import multiprocessing
import logging

logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

NUM_CHANNELS = 2
SAMPLE_RATE = 44100
NUM_SECONDS = 3

NUM_FRAMES = 1024
SOUND_THRESHOLD = 300
MAX_PERCENT_SILENT = 0.75

INPUT_SIZE = int(SAMPLE_RATE * NUM_SECONDS)
KERNEL_SIZE = int((SAMPLE_RATE / 100) * 2)  # 20 milliseconds
STRIDE = int(KERNEL_SIZE / 2)

BATCH_SIZE = 32
NUM_LABELS = 2

_PATIENCE_THRESHOLD_MINS = (60 * 2.5)  # 2.5 hours
PATIENCE_MAX_MINS = (_PATIENCE_THRESHOLD_MINS * 1.5)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TELEGRAM_ID = "TELEGRAM_ID"
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"

TELEGRAM_INTERVAL_MINUTES = 2
TELEGRAM_INTERVAL_SECONDS = (TELEGRAM_INTERVAL_MINUTES * 60)

MODEL_FILE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "..",  # src
    "..",  # sound-detection
    "model",
    "pytorch_model.pt"
)

LABEL_MAP_FILE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "..",  # src
    "..",  # sound-detection
    "model",
    "labels.json"
)
