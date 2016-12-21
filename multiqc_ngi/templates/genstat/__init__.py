#!/usr/bin/env python

"""
=============
 genstat
=============

This theme generates a Tornado web page template, for use in
Genomics Status - the sample tracking website used by the
National Genomics Infrastructure. The NGI is part of the Science for
Life Laboratory in Stockholm, Sweden.

"""
import os

template_parent = 'default'

template_dir = os.path.dirname(__file__)
base_fn = 'base.html'
