import logging

logging.basicConfig(
    level=logging.CRITICAL,
    format="[\033[92m%(levelname)s %(asctime)s\033[0m]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

logger = logging.getLogger()
