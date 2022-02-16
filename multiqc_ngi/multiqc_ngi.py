#!/usr/bin/env python
""" MultiQC hook functions - we tie into the MultiQC
core here to add in extra functionality. """

from __future__ import print_function
from collections import OrderedDict
from couchdb import Server
import logging
import json
import os
import re
import requests
import socket
import subprocess
import yaml

from pkg_resources import get_distribution
__version__ = get_distribution("multiqc_ngi").version

from multiqc.utils import report, util_functions, config

log = logging.getLogger('multiqc')

report.ngi = dict()

# Add default config options for the things that are used in MultiQC_NGI
def multiqc_ngi_config():
    """ Set up MultiQC config defaults for this package """

    # Use the NGI template by default
    config.template = 'ngi'

    # Push parsed results to StatusDB
    config.push_statusdb = True

    # Additional filename cleaning for NGI pipelines
    config.fn_clean_exts.extend([
        '.bowtie_log',
        '.featureCounts'
    ])

    # Ignore intermediate files from WGS Piper results
    config.fn_ignore_paths.extend([
        '*/piper_ngi/01_raw_alignments/*',
        '*/piper_ngi/02_preliminary_alignment_qc/*',
        '*/piper_ngi/03_genotype_concordance/*',
        '*/piper_ngi/04_merged_alignments/*'
    ])

    # Save generated reports remotely on the tools server
    config.save_remote = False
    config.remote_sshkey = None
    config.remote_port = None
    config.remote_destination = None

    # General MultiQC_NGI options
    config.disable_ngi = False


# NGI specific code to run after the modules have finished
class ngi_metadata():

    def __init__(self):

        log.debug("Running MultiQC_NGI v{} (after modules)".format(__version__))

        # Global try statement to catch any unhandled exceptions and stop MultiQC from crashing
        try:

            # Flags - overwritten when stuff works
            report.ngi['ngi_header'] = False

            # Check that we're not ignoring NGI module with a command line flag
            if config.kwargs.get('disable_ngi', False) is True:
                log.info("Skipping MultiQC_NGI as specified on command line")
                return None

            # Check that these hooks haven't been disabled in the config file
            if getattr(config, 'disable_ngi', False) is True:
                log.debug("Skipping MultiQC_NGI as specified in config file")
                return None

            # Run WGS Piper specific cleanup
            for f in report.searchfiles:
                if 'piper_ngi' in f[1].split(os.sep):
                    log.info("Looks like WGS data - cleaning up report")
                    self.ngi_wgs_cleanup()
                    break

            # Are we using the dummy test data?
            self.couch = None
            self.test_data = None
            if 'test_database' in config.kwargs and config.kwargs['test_database'] is not None:
                log.info("Using test data instead of connecting to StatusDB: {}".format(config.kwargs['test_database']))
                with open(config.kwargs['test_database'], 'r') as tdata:
                    self.test_data = json.loads(tdata.read())
            else:
                # Connect to StatusDB
                self.couch = self.connect_statusdb()

            # Load and process the data
            if self.couch is not None or self.test_data is not None:

                # Get project ID
                pids = None
                if 'project' in config.kwargs and config.kwargs['project'] is not None:
                    log.info("Using supplied NGI project id: {}".format(config.kwargs['project']))
                    pids = config.kwargs['project']
                    self.s_names = set()
                    for x in report.general_stats_data:
                        self.s_names.update(x.keys())
                else:
                    pids = self.find_ngi_project()

                if len(pids) == 1:
                    pid = list(pids.keys())[0]
                    log.info("Found one NGI project id: {}".format(pid))

                    # Get the metadata for the project
                    self.get_ngi_project_metadata(pid)
                    self.get_ngi_samples_metadata(pid)

                    # Find reference genome and append it to the Fastqscreen html
                    self.fastqscreen_genome()

                    # Add to General Stats table
                    self.general_stats_sample_meta()

                    # Push MultiQC data to StatusDB
                    if getattr(config, 'push_statusdb', None) is None:
                        config.push_statusdb = False
                    if config.kwargs.get('push_statusdb', None) is not None:
                        config.push_statusdb = config.kwargs['push_statusdb']
                    if config.push_statusdb:
                        self.push_statusdb_multiqc_data()
                    else:
                        log.info("Not pushing results to StatusDB. To do this, use --push or set config push_statusdb: True")

                elif len(pids) > 1:
                    log.info("Found {} NGI project IDs: {}".format(len(pids), ", ".join(pids)))
                    for pid, s_names in pids.items():
                        self.get_ngi_samples_metadata(pid, s_names)
                    self.general_stats_sample_meta()
                else:
                    log.info("No NGI project IDs found.")


        except Exception as e:
            log.error("MultiQC_NGI v{} crashed! Skipping...".format(__version__))
            log.exception(e)
            log.error("Continuing with base MultiQC execution.")


    def ngi_wgs_cleanup(self):
        """ WGS Piper specific cleanup steps.
        - Clean up sample names to just the NGI sample ID in general stats
        - Remove FastQC results from the general statistics table (lane level)
        """
        # Remove FastQC and FastQ_screen from General Stats
        del_idx = list()
        for idx, h in enumerate(report.general_stats_headers):
            for col in h.values():
                if col.get('namespace') == 'FastQC':
                    del_idx.append(idx)
                    break
                if col.get('namespace') == 'FastQ Screen':
                    del_idx.append(idx)
                    break
        for i in del_idx:
            del report.general_stats_headers[i]
            del report.general_stats_data[i]

        for x, data in enumerate(report.general_stats_data):
            new_d = {}
            for s_name in report.general_stats_data[x].keys():
                m = re.search(r'(P\d{3,5}_\d{3,6})', s_name)
                if m:
                    s = m.group(1)
                else:
                    s = s_name
                new_d[s] = report.general_stats_data[x][s_name]

            report.general_stats_data[x] = new_d


    def find_ngi_project(self):
        """ Try to find a NGI project ID in the sample names.
        If just one found, add to the report header. """

        # Collect sample IDs
        self.s_names = set()
        for x in report.general_stats_data:
            self.s_names.update(x.keys())
        for d in report.saved_raw_data.values():
            try:
                self.s_names.update(d.keys())
            except AttributeError:
                pass
        pids = dict()
        for s_name in self.s_names:
            m = re.search(r'(P\d{3,5})', s_name)
            if m:
                try:
                    pids[m.group(1)].append(s_name)
                except KeyError:
                    pids[m.group(1)] = [s_name]
        return pids


    def get_ngi_project_metadata(self, pid):
        """ Get project metadata from statusdb """
        if self.test_data is not None:
            p_summary = self.test_data['summary']
        else:
            if self.couch is None:
                return None
            try:
                p_view = self.couch['projects'].view('project/summary')
            except socket.error:
                log.error('CouchDB Operation timed out')
            p_summary = None
            for row in p_view:
                if row['key'][1] == pid:
                    p_summary = row

            try:
                p_summary = p_summary['value']
            except TypeError:
                log.error("statusdb returned no rows when querying {}".format(pid))
                return None
            log.debug("Found metadata for NGI project '{}'".format(p_summary['project_name']))

        config.title = '{}: {}'.format(pid, p_summary['project_name'])
        config.project_name = p_summary['project_name']
        config.output_fn_name = '{}_{}'.format(p_summary['project_name'], config.output_fn_name)
        config.data_dir_name = '{}_{}'.format(p_summary['project_name'], config.data_dir_name)
        log.debug("Renaming report filename to '{}'".format(config.output_fn_name))
        log.debug("Renaming data directory to '{}'".format(config.data_dir_name))

        report.ngi['pid'] = pid
        report.ngi['project_name'] = p_summary['project_name']
        keys = {
            'contact_email':'contact',
            'application':'application',
            'reference_genome':'reference_genome'
        }
        d_keys = {
            'customer_project_reference': 'customer_project_reference',
            'project_type': 'type',
            'sequencing_platform': 'sequencing_platform',
            'sequencing_setup': 'sequencing_setup',
            'libprep':'library_construction_method'

            }
        for i, j in keys.items():
            try:
                report.ngi[i] = p_summary[j]
                report.ngi['ngi_header'] = True
            except KeyError:
                log.warn("Couldn't find '{}' in project summary".format(j))
        for i, j in d_keys.items():
            try:
                report.ngi[i] = p_summary['details'][j]
                report.ngi['ngi_header'] = True
            except KeyError:
                log.warn("Couldn't find '{}' in project details".format(j))


    def get_ngi_samples_metadata(self, pid, s_names=None):
        """ Get project sample metadata from statusdb """
        if self.test_data is not None:
            report.ngi['sample_meta'] = self.test_data['samples']
        elif self.couch is not None:
            p_view = self.couch['projects'].view('project/samples')
            p_samples = p_view[pid]
            if not len(p_samples.rows) == 1:
                log.error("statusdb returned {} rows when querying {}".format(len(p_samples.rows), pid))
            else:
                if 'sample_meta' not in report.ngi:
                    report.ngi['sample_meta'] = dict()
                report.ngi['sample_meta'].update(p_samples.rows[0]['value'])

        if 'ngi_names' not in report.ngi:
            report.ngi['ngi_names'] = dict()
        for s_name, s in report.ngi.get('sample_meta', {}).items():
            report.ngi['ngi_names'][s_name] = s.get('customer_name', '???')
        report.ngi['ngi_names_json'] = json.dumps(report.ngi['ngi_names'], indent=4)


    def fastqscreen_genome(self):
        """Add the Refrence genome from statusdb to fastq_screen html"""
        if report.ngi.get('reference_genome') is not None:
            for m in report.modules_output:
                if m.anchor  == 'fastq_screen':
                    genome=report.ngi['reference_genome']
                    nice_names = {
                            'hg19':'Human',
                            'GRCh37':'Human',
                            'mm9':'Mouse',
                            'GRCm38':'Mouse',
                            'sacCer2':'S.Cerevisiae',
                            'canFam3':'C.Familiaris - Dog',
                            'dm3':'D.melanogaster - Fruit fly'
                              }
                    if genome in nice_names.keys():
                          genome = nice_names[genome]
                    m.intro += '<p style="margin-top:20px;" class="text-info"> <span class="glyphicon glyphicon-piggy-bank"></span>  The reference genome in Genomic status is {}</p>'.format(genome)


    def general_stats_sample_meta(self):
        """ Add metadata about each sample to the General Stats table """

        meta = report.ngi.get('sample_meta')
        if meta is not None and len(meta) > 0:

            log.info('Found {} samples in StatusDB'.format(len(meta)))

            # Write to file
            util_functions.write_data_file(meta, 'ngi_meta')

            # Add to General Stats table
            gsdata = dict()
            formats = dict()
            s_names = dict()
            ngi_ids = dict()
            conc_units = ''
            for sid in meta:

                # Find first sample name matching this sample ID
                s_name = None
                for x in sorted(self.s_names):
                    if sid in x:
                        s_name = x
                        s_names[s_name] = x
                        ngi_ids[s_name] = sid
                        break

                # Skip this sample if we don't have any matching data
                if s_name is None:
                    log.debug("Skipping StatusDB metadata for sample {} as no bioinfo report logs found.".format(sid))
                    continue

                # Make a dict to hold new data for General Stats
                gsdata[s_name] = dict()

                # NGI name
                try:
                    gsdata[s_name]['user_sample_name'] = report.ngi['ngi_names'][ngi_ids[s_name]]
                except KeyError:
                    pass

                # RIN score
                try:
                    gsdata[s_name]['initial_qc_rin'] = meta[sid]['initial_qc']['rin']
                except KeyError:
                    pass

                # Try to figure out which library prep was used
                seq_lp = None
                for lp in sorted(meta[sid].get('library_prep', {}).keys()):
                    try:
                        if len(meta[sid]['library_prep'][lp]['sample_run_metrics']) > 0:
                            if seq_lp is None:
                                seq_lp = lp
                            else:
                                seq_lp = None
                                log.warn('Found multiple sequenced lib preps for {} - skipping metadata'.format(sid))
                                break
                    except KeyError:
                        pass
                if seq_lp is not None:
                    try:
                        if meta[sid]['library_prep'][lp]['amount_taken_(ng)'] is not None:
                            gsdata[s_name]['amount_taken'] = meta[sid]['library_prep'][lp]['amount_taken_(ng)']
                    except KeyError:
                        pass
                    try:
                        for lv in sorted(meta[sid]['library_prep'][lp]['library_validation'].keys()):
                            gsdata[s_name]['lp_concentration'] = meta[sid]['library_prep'][lp]['library_validation'][lv]['concentration']
                            formats[s_name] = meta[sid]['library_prep'][lp]['library_validation'][lv]['conc_units']
                    except KeyError:
                        pass

            log.info("Matched meta for {} samples from StatusDB with report sample names".format(len(s_names)))
            if len(s_names) == 0:
                return None

            # Deal with having more than one initial QC concentration unit
            formats_set = set(formats.values())
            if len(formats_set) > 1:
                log.warning("Mixture of library_validation concentration units! Found: {}".format(", ".join(formats_set)))
                for s_name in gsdata:
                    try:
                        gsdata[s_name]['lp_concentration'] = '{} {}'.format(gsdata[s_name]['lp_concentration'], formats[s_name])
                    except KeyError:
                        pass
            elif len(formats_set) == 1:
                conc_units = formats_set.pop()

            # Decide on whether to show or hide conc & amount taken based on range
            conc_hidden = True
            amounts_hidden = True
            try:
                concs = [gsdata[x]['lp_concentration'] for x in gsdata]
                if max(concs) - min(concs) > 50:
                    conc_hidden = False
            except (KeyError, ValueError):
                conc_hidden = False
            try:
                amounts = [gsdata[x]['amount_taken'] for x in gsdata]
                if max(amounts) - min(amounts) > 10:
                    amounts_hidden = False
            except KeyError:
                amounts_hidden = False

            # Prepend columns to the General Stats table (far left)
            gsheaders_prepend = OrderedDict()
            gsheaders_prepend['user_sample_name'] = {
                'namespace': 'NGI',
                'title': 'Name',
                'description': 'User sample ID',
                'scale': False
            }
            report.general_stats_data.insert(0, gsdata)
            report.general_stats_headers.insert(0, gsheaders_prepend)

            # Add columns to the far right of the General Stats table
            gsheaders = OrderedDict()
            gsheaders['initial_qc_rin'] = {
                'namespace': 'NGI',
                'title': 'RIN',
                'description': 'Initial QC: RNA Integrity Number',
                'min': 0,
                'max': 10,
                'scale': 'YlGn',
                'format': '{:,.2f}'
            }
            gsheaders['lp_concentration'] = {
                'namespace': 'NGI',
                'title': 'Lib Conc. ({})'.format(conc_units),
                'description': 'Library Prep: Concentration ({})'.format(conc_units),
                'min': 0,
                'scale': 'YlGn',
                'format': '{:.,0f}',
                'hidden': conc_hidden
            }
            gsheaders['amount_taken'] = {
                'namespace': 'NGI',
                'title': 'Amount Taken (ng)',
                'description': 'Library Prep: Amount Taken (ng)',
                'min': 0,
                'scale': 'YlGn',
                'format': '{:.,0f}',
                'hidden': amounts_hidden
            }
            report.general_stats_data.append(gsdata)
            report.general_stats_headers.append(gsheaders)



    def push_statusdb_multiqc_data(self):
        """ Push data parsed by MultiQC modules to the analysis database
        in statusdb. """

        # StatusDB view code for analysis/project_id view:
        # function(doc) {
        #   var project_id=Object.keys(doc.samples)[0].split('_')[0];
        #   emit(project_id, doc);
        # }

        # Connect to the analysis database
        if self.couch is None:
            return None
        try:
            db = self.couch['analysis']
            p_view = db.view('project/project_id')
        except socket.error:
            log.error('CouchDB Operation timed out')
            return None

        # Try to get an existing document if one exists
        doc = {}
        for row in p_view:
            if row['key'] == report.ngi['pid']:
                doc = row.value
                break

        # Start fresh unless the existing doc looks similar
        newdoc = {
            'entity_type': 'MultiQC_data',
            'project_id': report.ngi['pid'],
            'project_name': report.ngi['project_name'],
            'MultiQC_version': config.version,
            'MultiQC_NGI_version': config.multiqc_ngi_version,
        }
        for k in newdoc.keys():
            try:
                assert(doc[k] == newdoc[k])
            except (KeyError, AssertionError):
                doc = newdoc
                log.info('Creating new analysis record in StatusDB')
                break
        if doc != newdoc:
            log.info('Updating existing analysis record in StatusDB')

        # Add sample metadata to doc
        if 'samples' not in doc:
            doc['samples'] = dict()
        for key, d in report.saved_raw_data.items():
            for s_name in d:
                m = re.search(r'(P\d{3,5}_\d{1,6})', s_name)
                if m:
                    sid = m.group(1)
                else:
                    sid = s_name
                if sid not in doc['samples']:
                    doc['samples'][sid] = dict()
                doc['samples'][sid][key] = d[s_name]

        # Save object to the database
        db.save(doc)


    def connect_statusdb(self):
        """ Connect to statusdb """
        try:
            conf_file = os.path.join(os.environ.get('HOME'), '.ngi_config', 'statusdb.yaml')
            with open(conf_file, "r") as f:
                sdb_config = yaml.safe_load(f)
                log.debug("Got MultiQC_NGI statusdb config from the home directory.")
        except IOError:
            log.debug("Could not open the MultiQC_NGI statusdb config file {}".format(conf_file))
            try:
                with open(os.environ['STATUS_DB_CONFIG'], "r") as f:
                    sdb_config = yaml.safe_load(f)
                    log.debug("Got MultiQC_NGI statusdb config from $STATUS_DB_CONFIG: {}".format(os.environ['STATUS_DB_CONFIG']))
            except (KeyError, IOError):
                log.debug("Could not get the MultiQC_NGI statusdb config file from env STATUS_DB_CONFIG")
                log.warn("Could not find a statusdb config file")
                return None
        try:
            couch_user = sdb_config['statusdb']['username']
            password = sdb_config['statusdb']['password']
            couch_url = sdb_config['statusdb']['url']
            port = sdb_config['statusdb']['port']
        except KeyError:
            log.error("Error parsing the config file {}".format(conf_file))
            return None

        server_url = "http://{}:{}@{}:{}".format(couch_user, password, couch_url, port)

        # First, test that we can see the server.
        try:
            requests.get(server_url, timeout=3)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            log.warn("Cannot contact statusdb - skipping NGI metadata stuff")
            return None

        return Server(server_url)



# NGI code to run once the report is finished and has been written to disk
class ngi_after_execution_finish():

    def __init__(self):
        log.debug("Running MultiQC_NGI v{} (after execution finish)".format(__version__))

        if config.kwargs.get('disable_ngi', False) is True:
            log.debug("Skipping MultiQC_NGI (after execution finish) as 'disable_ngi' was specified")
            return None

        # Global try statement to catch any unhandled exceptions and stop MultiQC from crashing
        try:

            # Copy finished reports to remote server
            if getattr(config, 'save_remote', False) is True:
                scp_command = ['scp']
                if getattr(config, 'remote_sshkey', None) is not None:
                    scp_command.extend(['-i', config.remote_sshkey])
                if getattr(config, 'remote_port', None) is not None:
                    scp_command.extend(['-P', str(config.remote_port)])
                scp_command.extend([config.output_fn, config.remote_destination])
                log.debug('Transferring report with command: {}'.format(' '.join(scp_command)))
                DEVNULL = open(os.devnull, 'wb')
                p = subprocess.Popen(scp_command, stdout=DEVNULL)
                pid, exit_status = os.waitpid(p.pid, 0)
                if exit_status != 0:
                    log.error("Not able to copy report to remote server: Subprocess command failed.")

        except Exception as e:
            log.error("MultiQC_NGI v{} crashed! Skipping...".format(__version__))
            log.exception(e)
            log.error("Continuing with base MultiQC execution.")
