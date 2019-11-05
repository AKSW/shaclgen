# -*- coding: utf-8 -*-
#%%
from setuptools import setup
setup(
    name = 'shapegen',
    version = '0.1.0',
    packages = ['shapegen'],
    entry_points = {
        'console_scripts': [
            'shapegen = shapegen.__main__:main'
        ]
    })
