#!/usr/bin/env python

""" MultiQC module to parse edgeR sample correlation output from NGI-RNAseq Pipeline """

from __future__ import print_function
from collections import OrderedDict
import logging

from multiqc import config
from multiqc.modules.base_module import BaseMultiqcModule

# Import the NGI-RNAseq submodules
from . import heatmap
from . import mds_plot

# Initialise the logger
log = logging.getLogger('multiqc.modules.ngi_rnaseq')

class MultiqcModule(BaseMultiqcModule):

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='NGI-RNAseq', anchor='ngi_rnaseq',
        href="https://github.com/SciLifeLab/NGI-RNAseq/",
        info=" is a Best Practice analysis pipeline, used at the SciLifeLab National Genomics Infrastructure for RNA-Seq.")

        # Set up class objects to hold parsed data
        self.sections = list()
        self.general_stats_headers = OrderedDict()
        self.general_stats_data = dict()
        n = dict()
        
        # Call submodule functions
        n['heatmaps'] = heatmap.parse_reports(self)
        if n['heatmaps'] > 0:
            log.info("Found {} heatmaps".format(n['heatmaps']))
        
        n['mds_plot'] = mds_plot.parse_reports(self)
        if n['mds_plot'] > 0:
            log.info("Found {} MDS plots".format(n['mds_plot']))
        
        # Exit if we didn't find anything
        if sum(n.values()) == 0:
            log.debug("Could not find any reports in {}".format(config.analysis_dir))
            raise UserWarning
        
        