#!/usr/bin/env python
""" MultiQC hook functions - we tie into the MultiQC
core here to add in extra functionality. """

import logging
from multiqc.utils import (report, config)

log = logging.getLogger('multiqc')

def after_modules():
  """ Plugin code to run when MultiQC modules have completed  """
  num_modules = len(report.modules_output)
  status_string = "MultiQC hook - {} modules repoted!".format(num_modules)
  log.critical(status_string)