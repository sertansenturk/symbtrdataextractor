#!/usr/bin/env python
from setuptools import setup
from setuptools import find_packages


setup(name='symbtrdataextractor',
      version='2.1.0',
      author='Sertan Senturk',
      author_email='contact AT sertansenturk DOT com',
      license='agpl 3.0',
      description='Tools to extract (meta)data related to SymbTr from the '
                  'information in score file and MusicBrainz',
      url='http://sertansenturk.com',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          "python-Levenshtein>=0.12.0",
          "networkx>=1.11",
          "numpy>=1.8.0"
      ],
      )
