import logging

SIMPLE_FORMAT = '%(asctime)s %(message)s'
VERBOSE_FORMAT = '%(asctime)s %(filename)s %(funcName)s %(levelname)s %(message)s'

logging.basicConfig(level=logging.DEBUG,
                    format=SIMPLE_FORMAT,
                    filemode='w')

log_inst = logging.getLogger('paper_plane')


