#!/usr/bin/env python

from importlib.metadata import version
from multiqc import config

__version__ = version("multiqc_ngi")
config.multiqc_ngi_version = __version__
