#!/usr/bin/env python

""" MultiQC module to parse output from featureCounts """

from __future__ import print_function
from collections import OrderedDict
import logging
import re

from multiqc import config, BaseMultiqcModule, plots

# Initialise the logger
log = logging.getLogger('multiqc')

class MultiqcModule(BaseMultiqcModule):

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='DupRadar',
        target="dupRadar", anchor='dupRadar',
        href='https://www.bioconductor.org/packages/release/bioc/html/dupRadar.html',
        info="provides duplication rate quality control for RNA-Seq datasets.")
        
        # Find and load any dupRadar int_slope reports
        try:
            intslope_sp = config.sp['ngi_rnaseq']['dupradar_intslope']
        except KeyError:
            intslope_sp = {'fn': '*intercept_slope.txt'}
        int_regex = r'(.*)- dupRadar Int \(duprate at low read counts\): ([\d\.]+)'
        slope_regex = r'(.*)- dupRadar Sl \(progression of the duplication rate\): ([\d\.]+)'
        self.dupradar_stats = dict()
        for f in self.find_log_files(intslope_sp):
            for l in f['f'].splitlines():
                # Intercept
                m = re.search(int_regex, l)
                if m:
                    s_name = self.clean_s_name(m.group(1), f['root'])
                    if s_name not in self.dupradar_stats:
                        self.dupradar_stats[s_name] = dict()
                    self.dupradar_stats[s_name]['int'] = m.group(2)
                
                # Slope
                m = re.search(slope_regex, l)
                if m:
                    s_name = self.clean_s_name(m.group(1), f['root'])
                    if s_name not in self.dupradar_stats:
                        self.dupradar_stats[s_name] = dict()
                    self.dupradar_stats[s_name]['slope'] = m.group(2)
        
        # Find and load any dupRadar GML line plots
        try:
            dupradar_line_sp = config.sp['ngi_rnaseq']['dupradar_intslope']
        except KeyError:
            dupradar_line_sp = {'fn': '*_duprateExpDensCurve.txt'}
        self.dupradar_plots = dict()
        for f in self.find_log_files(dupradar_line_sp):
            self.dupradar_plots[f['s_name']] = dict()
            for l in f['f'].splitlines():
                s = l.split()
                try:
                    self.dupradar_plots[f['s_name']][float(s[0])] = float(s[1])
                except (ValueError, IndexError):
                    pass
        
        # Add Int to General Stats table
        
        # Create line plot of GML lines
        
        