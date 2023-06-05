from setuptools import setup

from db2 import __version__

setup(
    name='db2',
    version=__version__,
    url='https://github.com/COPLIN-UFSM/db2',
    author='Henry Cagnini',
    author_email='henry.cagnini@ufsm.br',
    py_modules=['db2'],
    install_requires=[
        'ibm_db',
    ],
)
