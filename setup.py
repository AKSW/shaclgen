# -*- coding: utf-8 -*-
#%%
from setuptools import setup


with open('README.rst') as readme:
    l_description = readme.read()
with open('requirements.txt') as reqs:
    requirements = reqs.read()

setup(
    name = 'shaclgen',
    version = '0.1.5',
    packages = ['shaclgen'],
    description='Shacl graph generator',
    long_description=l_description,
    author='Alexis Keely',
    url='https://github.com/alexiskeely/shaclgen',
    author_email='alexiskm@uw.com',
    install_requires=requirements,
    keywords=['Linked Data', 'Semantic Web', 'Python',
              'SHACL', 'Shapes', 'Schema', 'Validate'],
    license='MIT',
    classifiers=[
                'Development Status :: 4 - Beta',
                'Programming Language :: Python :: 3',

    ],
    entry_points = {
        'console_scripts': [
            'shaclgen = shaclgen.__main__:main'
        ]
    })
