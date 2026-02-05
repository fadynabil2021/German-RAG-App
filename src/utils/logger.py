import logging
import json
import os
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for unified logging.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging(level=logging.INFO):
    """
    Configures the root logger to use JSON formatting if in production.
    """
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatting in production environment
    if os.getenv("ENV") == "production":
        handler.setFormatter(JSONFormatter())
    else:
        # Standard readable formatting for dev
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
    logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True
    )
    
    # Silence third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)
