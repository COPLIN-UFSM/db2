from setuptools import setup

setup(
    name='db2',
    version='1.1',
    url='https://github.com/COPLIN-UFSM/db2',
    author='Henry Cagnini',
    author_email='henry.cagnini@ufsm.br',
    py_modules=['db2'],
    install_requires=['ibm_db==3.*'],
    python_requires='>=3.6.*, < 3.7',
)
