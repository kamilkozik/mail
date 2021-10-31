import logging

LOG_FORMAT = "[%(asctime)s %(levelname)s] %(name)s: %(message)s"


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_fmt = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    stream_handler.setFormatter(stream_fmt)
    logger.addHandler(stream_handler)

    return logger
