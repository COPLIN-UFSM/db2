import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent

about = dict()
with open(os.path.join(this_directory, 'db2', '__version__.py'), 'r', encoding='utf-8') as read_file:
    exec(read_file.read(), about)

with open(os.path.join(this_directory, 'README.md'), 'r', encoding='utf-8') as read_file:
    long_description = read_file.read()

install_requires = [
    'numpy',
    'pandas',
    'ibm_db==3.1.4; platform_system == "Windows"',
    'ibm_db; platform_system != "Windows"'
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    url=about['__url__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    description=about['__description__'],
    long_description_content_type='text/markdown',
    long_description=long_description,
    license=about['__license__'],
    packages=find_packages(include=['db2', 'db2.*']),
    py_modules=['db2'],
    install_requires=install_requires,
    python_requires='>=3.8,<3.12',
    include_package_data=True
)