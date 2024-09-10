import logging

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'

logging.basicConfig(format=log_format, level=logging.INFO)
logger = logging.getLogger(__name__)
