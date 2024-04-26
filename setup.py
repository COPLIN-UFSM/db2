from setuptools import setup
import os
from pathlib import Path

this_directory = Path(__file__).parent

with open(os.path.join(this_directory, 'README.md'), 'r', encoding='utf-8') as read_file:
    long_description = read_file.read()

setup(
    name='coplin_db2',
    version='1.4.3.5',
    url='https://github.com/COPLIN-UFSM/db2',
    author='Henry Cagnini',
    author_email='henry.cagnini@ufsm.br',
    description='Um módulo de conveniência para manipulação de bancos de dados IBM DB2 em Python.',
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=['db2', 'db2.utils'],
    py_modules=['db2'],
    install_requires=['ibm_db==3.1.4', 'numpy', 'pandas'],
    python_requires='>=3.8,<3.12'
)
