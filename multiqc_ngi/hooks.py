#!/usr/bin/env python
""" MultiQC hook functions - we tie into the MultiQC
core here to add in extra functionality. """

from couchdb import Server
import logging
import os
import re
import yaml

from multiqc.utils import (report, config)

log = logging.getLogger('multiqc')

def find_ngi_project():
  """ Try to find a NGI project ID in the sample names.
  If just one found, add to the report header. """
  project_ids = set()
  for s_name in report.general_stats_raw:
    m = re.search(r'(P\d{3,5})', s_name)
    if m:
      project_ids.add(m.group(1))
  project_ids = list(project_ids)
  if len(project_ids) == 1:
    log.info("Found one NGI project id: {}".format(project_ids[0]))
    add_project_header(project_ids[0])
  elif len(project_ids) > 1:
    log.warn("Multiple NGI project IDs found! {}".format(",".join(project_ids)))
  else:
    log.info("No NGI project IDs found.")


def add_project_header(pid):
  """ Add NGI project information to report header """
  meta = get_ngi_project_metadata(pid)


def get_ngi_project_metadata(pid):
  """ Get project metadata from statusdb """
  couch = connect_statusdb()
  if couch is None:
    return None
  p_view = couch['projects'].view('project/summary')
  p_summary = None
  for row in p_view:
    if row['key'][1] == pid:
      p_summary = row
  
  try:
    p_summary = p_summary['value']
  except TypeError:
    log.error("statusdb returned no rows when querying {}".format(pid))
    return None
  
  log.info("Found metadata for NGI project '{}'".format(p_summary['project_name']))
  
  config.title = p_summary['project_name']
  report.ngi = {'pid': pid}
  keys = {
    'contact_email':'contact',
    'application': 'application'
  }
  d_keys = {
    'customer_project_reference': 'customer_project_reference',
    'project_type': 'type',
    'sequencing_platform': 'sequencing_platform',
    'sequencing_setup': 'sequencing_setup'
  }
  for i, j in keys.items():
    try:
      report.ngi[i] = p_summary[j]
    except KeyError:
      raise
  for i, j in d_keys.items():
    try:
      report.ngi[i] = p_summary['details'][j]
    except KeyError:
      raise

  # import json
  # print(json.dumps(p_summary, indent=4))


def get_ngi_samples_metadata(pid):
  """ Get project sample metadata from statusdb """
  couch = connect_statusdb()
  if couch is None:
    return None
  p_view = couch['projects'].view('project/samples')
  p_samples = p_view[pid]
  if not len(p_samples.rows) == 1:
    log.error("statusdb returned {} rows when querying {}".format(len(p_samples.rows), pid))
    return None
  return p_samples.rows[0]['value']
  
  
  # for s_name in p_samples:
  #   self.general_stats_addcols(self.bismark_data['alignment'], headers['alignment'], 'bismark_alignment')
  # print("\n".join(p_samples.keys()))


def connect_statusdb():
  """ Connect to statusdb """
  try:
    conf_file = os.path.join(os.environ.get('HOME'), '.multiqc_ngi')
    with open(conf_file, "r") as f:
      config = yaml.load(f)
  except IOError:
    log.error("Could not open the config file {}".format(conf_file))
    return None
  if config['couch_user'] is None or config['password'] is None or config['couch_server'] is None:
    log.error("Error parsing the config file {}".format(conf_file))
    return None
  return Server("http://{}:{}@{}".format(config['couch_user'], config['password'], config['couch_server']))


  
