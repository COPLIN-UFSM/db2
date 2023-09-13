from setuptools import setup

setup(
    name='db2',
    version='1.2',
    url='https://github.com/COPLIN-UFSM/db2',
    author='Henry Cagnini',
    author_email='henry.cagnini@ufsm.br',
    py_modules=['db2'],
    install_requires=['ibm_db'],
    python_requires='>=3.7, <= 3.11',
)
