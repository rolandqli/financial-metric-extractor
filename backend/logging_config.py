import logging
from logging.handlers import RotatingFileHandler
import sys

# Create logger
logger = logging.getLogger("pdf_extractor")
logger.setLevel(logging.INFO)  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# Print to terminal
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_format)

# Write to file
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
