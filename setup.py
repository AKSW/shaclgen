# -*- coding: utf-8 -*-
#%%
from setuptools import setup
setup(
    name = 'shaclgen',
    version = '0.1.0',
    packages = ['shaclgen'],
    description='Shacl graph generator',
    author='Alexis Keely',
    author_email='alexiskm@uw.com',
    license='MIT',
    entry_points = {
        'console_scripts': [
            'shaclgen = shaclgen.__main__:main'
        ]
    })
