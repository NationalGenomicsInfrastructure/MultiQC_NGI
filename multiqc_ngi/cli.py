#!/usr/bin/env python
""" MultiQC command line options - we tie into the MultiQC
core here and add some new command line parameters. """

import click

disable_ngi = click.option('--disable-ngi', 'disable_ngi',
    is_flag = True,
    help = "Disable the MultiQC_NGI plugin on this run"
)
pid_option = click.option('--project',
    type = str,
    help = 'Manually specify a project in StatusDB instead of detecting automatically'
)
push_flag = click.option('--push/--no-push', 'push_statusdb',
    default = None,
    help = 'Push / do not push MultiQC results to StatusDB analysis db. Overrides config option push_statusdb'
)
test_db = click.option('--test-db', 'test_database',
    default = None,
    help = "Path to a static file to use for testing instead of StatusDB. Useful for testing when the NGI database isn't accessible."
)
