#!/usr/bin/env python

""" MultiQC module to parse output from featureCounts """

from __future__ import print_function
from collections import OrderedDict
import logging

from multiqc import config
from multiqc.plots import bargraph
from multiqc.modules.base_module import BaseMultiqcModule


# Initialise the logger
log = logging.getLogger('multiqc')

class MultiqcModule(BaseMultiqcModule):

    def __init__(self):

        # Initialise the parent object
        super(MultiqcModule, self).__init__(name='Biotype Counts',
        target="featureCounts_biotype", anchor='featurecounts_biotype',
        href='http://bioinf.wehi.edu.au/featureCounts/',
        info="counts mapped reads overlapping genomic features. ")

        # Find and load any featureCounts reports
        self.featurecounts_biotype_data = dict()
        for f in self.find_log_files('ngi_rnaseq/featureCounts_biotype'):
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
        self.add_section(
            description = "This plot shows reads overlapping features of different biotypes.",
            plot = self.featureCounts_biotypes_chart()
        )


    def parse_featurecounts_report (self, f):
        """
        Parse the featureCounts file.
        NB: This is NOT the summary file as in the main featureCounts module.
        """
        parsed_data = dict()
        for l in f['f'].splitlines():
            s = l.split("\t")
            try:
                parsed_data[s[0]] = int(s[1])
            except (IndexError, ValueError):
                pass

        # Collect total count number
        total_count = 0
        for k in parsed_data:
            total_count += parsed_data[k]

        # Calculate the percent aligned if we can
        if 'rRNA' in parsed_data:
            parsed_data['percent_rRNA'] = (float(parsed_data['rRNA'])/float(total_count)) * 100.0

        # Add to the main dictionary
        if len(parsed_data) > 1:
            if f['s_name'] in self.featurecounts_biotype_data:
                log.debug("Duplicate sample name found! Overwriting: {}".format(f['s_name']))
            self.add_data_source(f, f['s_name'])
            self.featurecounts_biotype_data[f['s_name']] = parsed_data


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
            'format': '{:.2f}%'
        }
        self.general_stats_addcols(self.featurecounts_biotype_data, headers)


    def featureCounts_biotypes_chart (self):
        """ Make the featureCounts assignment rates plot """
        #Order keys the same everytime
        keys = OrderedDict()
        fixedorder = ['protein_coding','rRNA','miRNA', 'antisense', 'misc_RNA', 'pseudogene', 'processed_transcript',
                'processed_transcript', 'processed_pseudogene', 'sense_intronic', 'sense_overlapping',
                'lincRNA', 'snoRNA', 'snRNA']
        for d in self.featurecounts_biotype_data.values():
            for j in fixedorder:
                if j in d and j not in keys.keys():
                    keys[j] = {'name': j.replace('_', ' ') }
            # Order remaining keys by count in first dataset
            for k in sorted(d, key=d.get, reverse=True):
                if k == 'percent_rRNA':
                    continue
                keys[k] = {'name': k.replace('_', ' ') }
            break

        # Config for the plot
        pconfig = {
            'id': 'featureCounts_biotype_plot',
            'title': 'featureCounts Biotypes',
            'ylab': '# Reads',
            'cpswitch_counts_label': 'Number of Reads'
        }
        return bargraph.plot(self.featurecounts_biotype_data, keys, pconfig)
