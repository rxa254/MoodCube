import os
import logging
from multiprocessing import current_process

level = os.getenv('LOG_LEVEL', 'INFO').upper()
fmt = '%(processName)-12s | %(message)s'
logging.basicConfig(format=fmt, level=level)
