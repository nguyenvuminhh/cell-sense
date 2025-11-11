import logging


def get_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,  # <- this ensures reconfiguration works every time
    )
    return logging.getLogger("myapp")
