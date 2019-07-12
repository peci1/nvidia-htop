#!/usr/bin/env python3

from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='nvidia-htop',
      version='1.0',
      description='A tool for enriching the output of nvidia-smi',
      long_description=long_description,
      scripts=['nvidia-htop.py'],
      install_requires=[
        "termcolor"
      ]
      )
