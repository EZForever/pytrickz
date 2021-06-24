#!/usr/bin/env python3

from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name = 'pytrickz',
    version = '0.0.1-indev+20210613',
    description = 'A library aimed for providing handy hacks for your daily coding task.',
    license = 'MIT',
    long_description = long_description,
    author = 'EZForever',
    author_email = None,
    url = 'https://github.com/EZForever',
    packages = [ 'pytrickz', 'pytrickz.extensions' ],
    install_requires = [ ],
    extras_require = { 'extend_builtins': [ 'forbiddenfruit' ] },
    scripts = [ ]
)

