#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import setuptools

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('LICENSE') as license_file:
    licence = license_file.read()

#requirements = [ ]
#setup_requirements = ['pytest-runner', ]
#test_requirements = ['pytest', ]

setuptools.setup(
    name='modelplotpy',
    author="Pieter Marcus",
    author_email='pb.marcus@hotmail.com',
    description="Build nice model plots",
#    install_requires=requirements,
    license=licence,
    long_description=readme + '\n\n' + history,
#    include_package_data=True,
#    keywords='modelplotpy',
    packages=setuptools.find_packages(),
#    setup_requires=setup_requirements,
#    test_suite='tests',
#    tests_require=test_requirements,
    url='https://github.com/pbmarcus/modelplotpy',
#    zip_safe=False,
    version='0.0.1'
)
