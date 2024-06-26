#!/usr/bin/env python
"""
MultiQC_NGI is a plugin for MultiQC, providing additional tools which are
specific to the National Genomics Infrastructure at the Science for Life
Laboratory in Stockholm, Sweden.

For more information about NGI, see http://www.scilifelab.se/platforms/ngi/
For more information about MultiQC, see http://multiqc.info
"""

from setuptools import setup, find_packages

version = '0.8.0'

setup(
    name = 'multiqc_ngi',
    version = version,
    author = 'Phil Ewels',
    author_email = 'phil.ewels@scilifelab.se',
    description = "MultiQC plugin for the National Genomics Infrastructure @ SciLifeLab Sweden",
    long_description = __doc__,
    keywords = 'bioinformatics',
    url = 'https://github.com/ewels/MultiQC_NGI',
    download_url = 'https://github.com/ewels/MultiQC_NGI/releases',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'couchdb',
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
