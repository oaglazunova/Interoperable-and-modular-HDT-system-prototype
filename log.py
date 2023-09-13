import logging

logging.basicConfig(
    filename='logging.log',
    level=logging.INFO,  # logging level is info or higher
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('my_logger')