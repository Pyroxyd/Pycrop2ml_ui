#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {# pkglts, pysetup.kwds
# format setup arguments
from os import walk
from os.path import *
from setuptools import setup, find_packages


short_descr = "A Python library to generate a user interface for Crop2ML"
readme = open('README.md').read()
history = open('HISTORY.rst').read()

# find packages
pkgs = find_packages('src')

pkg_data = {}

nb = len(normpath(abspath("src/pycrop2ml_ui"))) + 1
data_rel_pth = lambda pth: normpath(abspath(pth))[nb:]

data_files = []
for root, dnames, fnames in walk("src/pycrop2ml_ui"):
    for name in fnames:
        if splitext(name)[-1] in [u'.json', u'.xml', u'.ini']:
            data_files.append(data_rel_pth(join(root, name)))


pkg_data['pycrop2ml_ui'] = data_files

setup_kwds = dict(
    name='pycrop2ml_ui',
    version="0.1.1",
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="Romaric JUSTES",
    author_email="romaric.justes@orange.fr",
    url='https://github.com/Pyroxyd/Pycrop2ml_ui',
    license='MIT',
    zip_safe=False,

    packages=pkgs,
    package_dir={'': 'src'},


    package_data=pkg_data,
    setup_requires=[
        "pytest-runner",
        ],
    install_requires=[
        ],
    tests_require=[
        "pytest",
        "pytest-mock",
        ],
    entry_points={},
    keywords='',
    )
# #}
# change setup_kwds below before the next pkglts tag

#setup_kwds["entry_points"] = {"console_scripts": ["cyml = pycropml.main:main"]}
setup_kwds["url"] = "https://github.com/Pyroxyd/Pycrop2ml_ui"
#setup_kwds["tests_require"] = ["pytest"]

# do not change things below
# {# pkglts, pysetup.call
setup(**setup_kwds)
# #}