#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('exodus/version.py', 'r') as f:
    exec(f.read())

setup(
    name='exodus',
    version=__version__,
    description='A light-weight, storage agnostic, data migration framework',
    license='BSD',
    author='Adam Griffiths',
    url='https://github.com/adamlwgriffiths/exodus',
    install_requires=['blist', 'import_file'],
    platforms=['any'],
    test_suite='tests',
    packages=['exodus'],
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
