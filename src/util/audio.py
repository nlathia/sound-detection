import torchaudio
import torch
import random
import os

from src.util.vars import (
    SAMPLE_RATE,
    INPUT_SIZE,
    logger
)


def convert_to_mp3(file_path):
    path_fields = os.path.split(file_path)
    file_name = path_fields[1].replace(".wav", ".mp3")
    result_file = os.path.join(path_fields[0], file_name)
    logger.info(f"🎧  Converting: {file_path} -> {result_file}")
    command = f"lame --preset standard \"{file_path}\" \"{result_file}\""
    result = os.system(command)
    logger.info(f"🎧  Converted to mp3 with result={result}")
    return result_file


def load_audio(file_path):
    logger.info(f"💾  Loading audio file from {file_path}...")
    sound, sampling_rate = torchaudio.load(file_path, normalization=True)
    assert sampling_rate == SAMPLE_RATE

    if sound.shape[1] < INPUT_SIZE:
        difference = INPUT_SIZE - sound.shape[1]
        padding = torch.zeros(sound.shape[0], difference)
        sound = torch.cat([sound, padding], 1)
    elif sound.shape[1] > INPUT_SIZE:
        random_idx = random.randint(0, sound.shape[1] - INPUT_SIZE)
        sound = sound.narrow(1, random_idx, INPUT_SIZE)

    assert sound.shape[1] == INPUT_SIZE
    return sound.unsqueeze(0)
