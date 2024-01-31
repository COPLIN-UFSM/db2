from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='db2',
    version='1.2',
    url='https://github.com/COPLIN-UFSM/db2',
    author='Henry Cagnini',
    author_email='henry.cagnini@ufsm.br',
    long_description=long_description,
    py_modules=['db2'],
    install_requires=['ibm_db==3.1.4'],
    python_requires='==3.11.*',
)
