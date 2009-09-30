#!/usr/bin/env python
"""
   Copyright 2008 Glencoe Software, Inc. All rights reserved.
   Use is subject to license terms supplied in LICENSE.txt

"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup
from omero_version import omero_version as ov

setup(name="OmeroWeb",
      version=ov,
      description="OmeroWeb",
      long_description="""\
OmeroWeb is the container of the web clients for OMERO."
""",
      author="Aleksandra Tarkowska",
      author_email="",
      url="https://trac.openmicroscopy.org.uk/omero/wiki/OmeroWeb",
      download_url="https://trac.openmicroscopy.org.uk/omero/wiki/OmeroWeb",
      packages=[''],
      test_suite='test.suite'
)

