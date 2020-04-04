import click

from src.alert.messenger import TelegramMessenger
from src.util.vars import (
    PATIENCE_MAX_MINS,
    logger
)
from src import (
    data_collection,
    classifier
)


@click.command()
@click.option('--classify/--no-classify', required=True, type=bool)
@click.option('--timeout', default=PATIENCE_MAX_MINS)
def run(classify: bool, timeout: int):
    """
    :param classify: Whether to just record (collect training data) or record + classify
    :param timeout: How long to run the pipeline for (default: just under 4 hours)
    """
    logger.info(f"ℹ️  Starting up...")
    messenger = TelegramMessenger()
    pipeline = classifier if classify else data_collection
    pipeline.run(messenger, timeout)
    logger.info(f"✅️  main() finished.")


if __name__ == "__main__":
    run()
