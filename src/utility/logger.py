import logging
import sys


# Create logger
logger = logging.getLogger("azure-network-ops")
logger.setLevel(logging.INFO)

# Stream handler (console)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
handler.setFormatter(formatter)

# Attach handler to logger
if not logger.hasHandlers():
    logger.addHandler(handler)
