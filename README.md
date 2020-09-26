# BeepNet Classifier

This repo contains the "Beep Net" pipeline, which records samples of audio, detects when there is a beep, and sends me a Telegram message.

The blog post that describes this hack project is here:

https://nlathia.github.io/2020/04/How-to-overengineer-a-sound-classifier.html

To get this running, you'll need to run the `install.sh` script, which assumes that you have `brew`, `pyenv`, `pyenv-virtualenv`, and Python 3.7.0 on your MacOS. It also installs `lame` via `brew` (to encode wav to mp3 files).

