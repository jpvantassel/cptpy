import logging

from .meta import __version__
from .cpt import CPT
from .cptu import CPTu

logging.getLogger('cptpy').addHandler(logging.NullHandler())