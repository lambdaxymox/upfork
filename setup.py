import sys
import setuptools
import os

from setuptools import setup
from setuptools.command.test import test as TestCommand


config = dict(
    description = 'Upfork is a script for automating git fork updates.',
    author = 'LambdaXymox',
    url = 'https://github.com/lambdaxymox/upfork',
    download_url = 'https://github.com/lambdaxymox/upfork.git',
    author_email = 'lambda.xymox@gmail.com',
    version = '0.1',
    install_requires = [],
    license = "LICENSE-APACHE",
    package_dir = {'': 'src'},
    packages = ['upfork'],
    scripts = [],
    name = 'upfork',
    tests_require = [],
    cmdclass = {},
    entry_points = {
        'console_scripts': [ 'upfork = upfork.upfork:main' ]
    }
)

setup(**config)

