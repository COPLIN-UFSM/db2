from setuptools import setup
import os
from pathlib import Path

this_directory = Path(__file__).parent

with open(os.path.join(this_directory, 'README.md'), 'r', encoding='utf-8') as read_file:
    long_description = read_file.read()

setup(
    name='db2',
    version='1.2',
    url='https://github.com/COPLIN-UFSM/db2',
    author='Henry Cagnini',
    author_email='henry.cagnini@ufsm.br',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['db2'],
    install_requires=['ibm_db==3.1.4'],
    python_requires='==3.11.*',
)
