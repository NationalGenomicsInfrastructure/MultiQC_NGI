#!/usr/bin/env python

from pkg_resources import get_distribution
from multiqc.utils import config

__version__ = get_distribution("multiqc_ngi").version
config.multiqc_ngi_version = __version__
