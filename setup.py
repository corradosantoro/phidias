#!/usr/bin/env python

from distutils.core import setup

setup(name='HEPHAESTUS',
      version='1.1.0',
      description='HEPHAESTUS is a dEclarative PytHon Agent Engine SupporTing mUlti-agent Systems',
      author='Corrado Santoro',
      author_email='santoro@dmi.unict.it',
      url='http://github.com/corradosantoro/hephaestus',
      packages=['hep'],
      package_dir={'hep': 'lib/hep' }
)
