import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid duplicating logs if the logger is already configured
    if not logger.handlers:
        logHandler = logging.StreamHandler(sys.stdout)
        
        # Consistent structured JSON logging format
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"}
        )
        
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)

    return logger
