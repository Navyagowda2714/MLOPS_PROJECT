import logging
import os
from datetime import datetime

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"),
    level=logging.INFO,
    format="[%(asctime)s]: %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
