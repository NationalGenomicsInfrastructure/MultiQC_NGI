#!/usr/bin/env python
"""
MultiQC_NGI is a plugin for MultiQC, providing additional tools which are
specific to the National Genomics Infrastructure at the Science for Life
Laboratory in Stockholm, Sweden.

Author: Phil Ewels

For more information about NGI, see http://www.scilifelab.se/platforms/ngi/
For more information about MultiQC, see http://multiqc.info
"""

import re
import subprocess

from setuptools import find_packages, setup


def get_version():
    try:
        # Get the git tag
        git_version = subprocess.check_output(["git", "describe", "--tags"]).strip().decode("utf-8")
        
        # Convert to PEP 440 compliant version
        # If format is like '0.8.0-26-gccd731d', convert to '0.8.0.dev26+gccd731d'
        match = re.match(r'([0-9]+\.[0-9]+\.[0-9]+)-([0-9]+)-g([0-9a-f]+)', git_version)
        if match:
            version, commits, sha = match.groups()
            return f"{version}.dev{commits}+g{sha}"
        
        # If it's just a clean tag like '0.8.0', use it directly
        if re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', git_version):
            return git_version
            
        # For any other format, use a simplified fallback
        return git_version.replace('-', '.').replace('g', '')
    except:
        # Fallback if git is not available
        return '0.1.0'

# Get the long description from the module docstring
long_description = __doc__ or ""

setup(
    name = 'multiqc_ngi',
    version = get_version(),
    description = "MultiQC plugin for the National Genomics Infrastructure @ SciLifeLab Sweden",
    long_description = long_description,
    keywords = 'bioinformatics',
    url = 'https://github.com/NationalGenomicsInfrastructure/MultiQC_NGI',
    download_url = 'https://github.com/NationalGenomicsInfrastructure/MultiQC_NGI/releases',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'ibmcloudant>=0.9.1',
        'simplejson',
        'pyyaml',
        'requests',
        'multiqc>=1.22.dev0'
    ],
    entry_points = {
        'multiqc.templates.v1': [
            'ngi = multiqc_ngi.templates.ngi',
            'genstat = multiqc_ngi.templates.genstat',
        ],
        'multiqc.cli_options.v1': [
            'disable = multiqc_ngi.cli:disable_ngi',
            'project = multiqc_ngi.cli:pid_option',
            'push_statusdb = multiqc_ngi.cli:push_flag',
            'test_db = multiqc_ngi.cli:test_db'
        ],
        'multiqc.hooks.v1': [
            'before_config = multiqc_ngi.multiqc_ngi:multiqc_ngi_config',
            'before_report_generation = multiqc_ngi.multiqc_ngi:ngi_metadata',
            'execution_finish = multiqc_ngi.multiqc_ngi:ngi_after_execution_finish'
        ]
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
