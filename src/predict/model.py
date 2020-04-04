import torch
import torch.nn as nn
import json
import os

from src.util.vars import (
    NUM_CHANNELS,
    KERNEL_SIZE,
    STRIDE,
    NUM_LABELS,
    MODEL_FILE_PATH,
    LABEL_MAP_FILE_PATH,
    DEVICE,
    logger
)


class BeepNet(nn.Module):

    def __init__(self):
        super(BeepNet, self).__init__()
        self.main = nn.Sequential(
            nn.Conv1d(
                in_channels=NUM_CHANNELS,
                out_channels=2,
                kernel_size=KERNEL_SIZE,
                stride=STRIDE
            ),
            nn.BatchNorm1d(num_features=NUM_CHANNELS),
            nn.MaxPool1d(kernel_size=2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(in_features=298, out_features=NUM_LABELS),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        batch_size = x.size(0)
        hidden = self.main(x)
        return self.classifier(hidden.view(batch_size, -1))


def load_model(file_path=MODEL_FILE_PATH, device=DEVICE):
    logger.info(f"💾  Loading model from {os.path.split(file_path)[1]}...")
    model = BeepNet()
    model.load_state_dict(torch.load(file_path))
    model.to(device)
    model.eval()
    return model


def load_labels(file_path=LABEL_MAP_FILE_PATH):
    logger.info(f"💾  Loading labels from {os.path.split(file_path)[1]}...")
    with open(file_path, "r") as lines:
        labels = json.loads(lines.read())
    return {int(k): bool(v) for k, v in labels.items()}
