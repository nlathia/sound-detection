from typing import Optional
from array import array
from datetime import datetime
import pyaudio
import time
import wave
import os

from src.util.vars import (
    NUM_CHANNELS,
    NUM_FRAMES,
    NUM_SECONDS,
    MAX_PERCENT_SILENT,
    SOUND_THRESHOLD,
)
from src.alert.messenger import TelegramMessenger
from src.util.vars import logger


def get_microphone(hardware: pyaudio.PyAudio):
    num_devices = hardware.get_device_count()
    for i in range(num_devices):
        device = hardware.get_device_info_by_index(i)
        if "microphone" in device['name'].lower():
            return device
    raise Exception("Microphone not found!")


def get_stream(hardware: pyaudio.PyAudio, rate: int):
    return hardware.open(
        format=pyaudio.paInt16,
        channels=NUM_CHANNELS,
        rate=rate,
        input=True,
        frames_per_buffer=NUM_FRAMES
    )


def record_sample(stream, rate, seconds=NUM_SECONDS):
    frames = []
    count_silent = 0
    for i in range(int(rate / NUM_FRAMES * NUM_SECONDS)):
        sound_data = array('h', stream.read(NUM_FRAMES, exception_on_overflow=False))
        if max(sound_data) < SOUND_THRESHOLD:
            count_silent += 1
        frames.append(sound_data)
    percent_silent = float(count_silent / len(frames))
    logger.info(f"ℹ️  Finished recording {seconds} seconds: {(percent_silent * 100):.2f}% silent.")
    return frames, percent_silent


def save_sample(frames, rate, sample_size):
    file_path = os.path.join(
        "data",
        "live",
        f"Sound-{str(datetime.now())}.wav"
    )
    logger.info(f"⤵️  Storing audio to: {file_path}...")
    wf = wave.open(file_path, "wb")
    wf.setnchannels(NUM_CHANNELS)
    wf.setsampwidth(sample_size)
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return file_path


def keep_recording(start_time: datetime, patience_threshold: int,
                   messenger: Optional[TelegramMessenger] = None) -> bool:
    minutes_running = (datetime.now() - start_time).seconds / 60

    if minutes_running > (patience_threshold * 0.75):
        # Starting to reach the patience limit!
        if minutes_running % 10 == 0 and messenger is not None:
            message = f"⏰ Still running after {int(minutes_running)} minutes."
            logger.info(message)
            messenger.send_alert(message, force_send=True)

    if minutes_running > patience_threshold:
        message = f"⏰ Running for {int(minutes_running)} minutes. Stopping."
        logger.info(message)
        if messenger is not None:
            messenger.send_alert(message, force_send=True)
        return False

    return True


def audio_files(patience_threshold: int, messenger: Optional[TelegramMessenger] = None):
    p = pyaudio.PyAudio()
    mic = get_microphone(p)
    sampling_rate = int(mic["defaultSampleRate"])
    sample_size = p.get_sample_size(pyaudio.paInt16)
    stream = get_stream(p, sampling_rate)

    start_time = datetime.now()
    try:
        while keep_recording(start_time, patience_threshold, messenger):
            frames, percent_silent = record_sample(stream, sampling_rate)
            if percent_silent <= MAX_PERCENT_SILENT:
                file_path = save_sample(frames, sampling_rate, sample_size)
                yield file_path
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info(f"🛑  Received keyboard interrupt. Stopping...")
    finally:
        logger.info(f"🛑  Cleaning up...")
        stream.stop_stream()
        stream.close()
        p.terminate()

    logger.info(f"✅  record_audio() finished.")
