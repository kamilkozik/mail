import logging

from settings import LOG_DIR, LOG_FORMAT


def get_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_DIR / 'ksbr_mail.log')

    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    c_formatter = logging.Formatter(LOG_FORMAT)
    f_formatter = logging.Formatter(LOG_FORMAT)

    c_handler.setFormatter(c_formatter)
    f_handler.setFormatter(f_formatter)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger
