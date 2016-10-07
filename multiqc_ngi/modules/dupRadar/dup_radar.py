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
        info="provides duplication rate quality control for RNA-Seq datasets. "
             "Highly expressed genes can be expected to have a lot of duplicate reads, "
             "but high numbers of duplicates at low read counts can indicate low library "
             "complexity with technical duplication.")
        
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
                    self.dupradar_stats[s_name]['dupRadar_int'] = m.group(2)
                
                # Slope
                m = re.search(slope_regex, l)
                if m:
                    s_name = self.clean_s_name(m.group(1), f['root'])
                    if s_name not in self.dupradar_stats:
                        self.dupradar_stats[s_name] = dict()
                    self.dupradar_stats[s_name]['dupRadar_slope'] = m.group(2)
        
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
        
        if len(self.dupradar_stats) == 0 and len(self.dupradar_plots) == 0:
            log.debug("Could not find any reports in {}".format(config.analysis_dir))
            raise UserWarning
        
        log.info("Found {} reports".format(max(len(self.dupradar_stats), len(self.dupradar_plots))))
        
        # Write parsed report data to a file
        self.write_data_file(self.dupradar_stats, 'multiqc_dupRadar')
        
        # Add Int to General Stats table
        headers = OrderedDict()
        headers['dupRadar_int'] = {
            'title': 'dupRadar Int',
            'description': 'Int (duprate at low read counts)',
            'min': 0,
            'scale': 'RdYlGn-rev',
            'format': '{:.2f}'
        }
        self.general_stats_addcols(self.dupradar_stats, headers)
        
        # Create line plot of GML lines
        # Only one section, so add to the intro
        pconfig = {
            'id': 'dupRadar_plot',
            'title': 'DupRadar General Linear Model',
            'ylab': '% duplicate reads',
            'xlab': 'expression (reads/kbp)',
            'ymax': 100,
            'ymin': 0,
            'xLog': True,
            'tt_label': '<b>{point.x:.0f} reads/kbp</b>: {point.y:,.2f}% duplicates',
            'xPlotLines': [{
                'value': 0.5,
                'color': 'green',
                'width': 1,
                'dashStyle': 'LongDash',
                'label': {
                    'text': '0.5 RPKM',
                    'verticalAlign': 'bottom',
                    'y': -65,
                    'style': {'color': 'green'}
                }
            },{
                'value': 1000,
                'color': 'red',
                'width': 1,
                'dashStyle': 'LongDash',
                'label': {
                    'text': '1 read/bp',
                    'verticalAlign': 'bottom',
                    'y': -65,
                    'style': {'color': 'red'}
                }
            }]
        }
        
        self.intro += plots.linegraph.plot(self.dupradar_plots, pconfig)
        
        