import logging 
import os
from dotenv import load_dotenv

load_dotenv()
level = os.getenv("LOG_LEVEL", "DEBUG")

# Create the root logger
root_logger = logging.getLogger('app')

# create console handler 
ch = logging.StreamHandler()

# Set root and console handler levels
match level.lower():
    case "debug":
        root_logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    case "info":
        root_logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    case "warning":
        root_logger.setLevel(logging.WARNING)
        ch.setLevel(logging.WARNING)
    case "error":
        root_logger.setLevel(logging.ERROR)
        ch.setLevel(logging.ERROR)
    case "critical":
        root_logger.setLevel(logging.CRITICAL)
        ch.setLevel(logging.CRITICAL)
    case _:
        root_logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s.%(module)s.%(funcName)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
root_logger.addHandler(ch)