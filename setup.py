#!/usr/bin/env python3

from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(name='nvidia-htop',
      version='1.0.2',
      description='A tool for enriching the output of nvidia-smi',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/peci1/nvidia-htop',
      author='Martin Pecka',
      author_email='peci1@seznam.cz',
      scripts=['nvidia-htop.py'],
      install_requires=[
        "termcolor"
      ],
      python_requires='>=3.5, <4',
      classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',
        'Environment :: GPU',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',

        'Topic :: System :: Monitoring',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Utilities',

        'License :: OSI Approved :: BSD License',

        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
      ],
      keywords='nvidia, nvidia-smi, GPU, htop, top',
      project_urls={
        'Bug Reports': 'https://github.com/peci1/nvidia-htop/issues',
        'Source': 'https://github.com/peci1/nvidia-htop',
      },
)
