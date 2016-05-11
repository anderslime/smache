import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__name__ = 'smache'
__version__ = '0.0.7'
__author__ = 'Anders Emil Nielsen'
__author_email__ = 'aemilnielsen@gmail.com'
__doc__ = """
Lots of description
"""


class ToxTestCommand(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        sys.exit(os.system('tox'))

setup(
    name=__name__,
    version=__version__,
    author=__author__,
    license='MIT',
    description=__doc__,
    packages=find_packages(exclude=['tests']),
    keywords='smart caching dataflow reactive push-based',
    long_description=open('README.rst').read(),
    install_requires=[
        'redis==2.10',
        'blinker==1.4',
        'mongoengine>=0.10.6,<0.11',
        'rq==0.5.6',
        'dagger'
    ],
    tests_require=['tox'],
    url='http://limecode.dk',
    cmdclass={'test': ToxTestCommand}
)
