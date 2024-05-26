import logging
import sys
from logging.handlers import RotatingFileHandler


def logger_activation():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a file handler with a maximum of 50 lines
    file_handler = RotatingFileHandler('magnit_parser.log', maxBytes=10240, backupCount=2, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Create a stream handler to display logs in the console
    stream_handler = logging.StreamHandler(sys.stdout)
    # stream_handler.setLevel(logging.DEBUG)  # You can set the level as needed
    stream_handler.setLevel(logging.INFO)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
