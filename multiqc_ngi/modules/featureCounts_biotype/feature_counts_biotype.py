#!/usr/bin/env python

""" MultiQC module to parse output from featureCounts """

from __future__ import print_function
from collections import OrderedDict
import logging

from multiqc import config, BaseMultiqcModule, plots

# Initialise the logger
log = logging.getLogger(__name__)

class MultiqcModule(BaseMultiqcModule):

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='featureCounts_biotype',
        anchor='featurecounts-biotype',
        href='http://bioinf.wehi.edu.au/featureCounts/',
        info="counts mapped reads overlapping genomic features. "\
        "This plot shows reads overlapping features of different biotypes.")
        
        # NGI specific search pattern
        try:
            sp = config.sp['ngi_rnaseq']['featureCounts_biotype']
        except KeyError:
            sp = {'fn': '*_biotype.featureCounts.txt'}
        
        # Find and load any featureCounts reports
        self.featurecounts_biotype_data = dict()
        self.featurecounts_keys = list()
        for f in self.find_log_files(config.sp['featurecounts_biotype']):
            self.parse_featurecounts_report(f)

        if len(self.featurecounts_biotype_data) == 0:
            log.debug("Could not find any reports in {}".format(config.analysis_dir))
            raise UserWarning

        log.info("Found {} reports".format(len(self.featurecounts_biotype_data)))

        # Write parsed report data to a file
        self.write_data_file(self.featurecounts_biotype_data, 'multiqc_featureCounts_biotype')

        # Basic Stats Table
        # Report table is immutable, so just updating it works
        self.featurecounts_biotypes_stats_table()

        # Assignment bar plot
        # Only one section, so add to the intro
        self.intro += self.featureCounts_biotypes_chart()


    def parse_featurecounts_report (self, f):
        """
        Parse the featureCounts file.
        NB: This is NOT the summary file as in the main featureCounts module.
        """
        
        file_names = list()
        parsed_data = dict()
        for l in f['f'].splitlines():
            s = l.split("\t")
            if len(s) < 6:
                continue
            # Don't keep massive lines in memory. Probably doesn't make much difference.
            del s[1:5]
            if s[0] == '# Program:featureCounts':
                for f_name in s[1:]:
                    file_names.append(f_name)
            else:
                k = s[0]
                parsed_data[k] = list()
                if k not in self.featurecounts_keys:
                    self.featurecounts_keys.append(k)
                for val in s[1:]:
                    parsed_data[k].append(int(val))
        
        suffix = 'Aligned.sortedByCoord.out.bam_biotype.featureCounts.txt'
        for idx, f_name in enumerate(file_names):
            
            # Clean up sample name
            s_name = self.clean_s_name(f_name, f['root'])
            if s_name.endswith(suffix):
                s_name = s_name[:-len(suffix)]
            
            # Reorganised parsed data for this sample
            # Collect total count number
            data = dict()
            data['Total'] = 0
            for k in parsed_data:
                data[k] = parsed_data[k][idx]
                data['Total'] += parsed_data[k][idx]
            
            # Calculate the percent aligned if we can
            if 'rRNA' in data:
                data['percent_rRNA'] = (float(data['rRNA'])/float(data['Total'])) * 100.0
            
            # Add to the main dictionary
            if len(data) > 1:
                if s_name in self.featurecounts_biotype_data:
                    log.debug("Duplicate sample name found! Overwriting: {}".format(s_name))
                self.add_data_source(f, s_name)
                self.featurecounts_biotype_data[s_name] = data
        

    def featurecounts_biotypes_stats_table(self):
        """ Take the parsed stats from the featureCounts report and add them to the
        basic stats table at the top of the report """
        
        headers = OrderedDict()
        headers['percent_rRNA'] = {
            'title': '% rRNA',
            'description': '% reads overlappying ribosomal RNA features',
            'max': 100,
            'min': 0,
            'suffix': '%',
            'scale': 'RdYlGn-rev',
            'format': '{:.1f}%'
        }
        self.general_stats_addcols(self.featurecounts_biotype_data, headers)


    def featureCounts_biotypes_chart (self):
        """ Make the featureCounts assignment rates plot """
        
        # Config for the plot
        config = {
            'id': 'featureCounts_biotype_plot',
            'title': 'featureCounts Biotypes',
            'ylab': '# Reads',
            'cpswitch_counts_label': 'Number of Reads'
        }
        
        return plots.bargraph.plot(self.featurecounts_biotype_data, self.featurecounts_keys, config)
