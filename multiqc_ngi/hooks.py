#!/usr/bin/env python
""" MultiQC hook functions - we tie into the MultiQC
core here to add in extra functionality. """

from multiqc import (logger, __version__)
from multiqc.utils import (report, config)
from multiqc.utils.log import init_log, LEVELS

def after_modules():
  """ Plugin code to run when MultiQC modules have completed  """
  print("MultiQC NGI plugin demonstration - {} modules repoted!".format(len(report.modules_output)))