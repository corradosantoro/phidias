#!/usr/bin/env python

from distutils.core import setup

setup(name='PHIDIAS',
      version='1.1.1',
      description='PytHon Interactive Declarative Intelligent Agent System',
      author='Corrado Santoro',
      author_email='santoro@dmi.unict.it',
      url='http://github.com/corradosantoro/phidias',
      packages=['phidias'],
      install_requires=[
            "requests",
            "parse",
            "prompt-toolkit"
      ],
      python_requires=">=3.6.0",
      package_dir={'phidias': 'lib/phidias'}
)
