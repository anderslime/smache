import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

__name__ = 'smache'
__version__ = '0.0.1'
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
    keywords='smart caching dataflow reactive push-based',
    install_requires=[
        'redis',
    ],
    tests_require=['tox'],
    url='http://limecode.dk',
    cmdclass={'test': ToxTestCommand}
)

