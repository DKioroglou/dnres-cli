from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1'
DESCRIPTION = 'Command line interface for dnres package.'
LONG_DESCRIPTION = 'A package that provides a command line interface to be used along with dnres python package.'

# Setting up
setup(
    name="dnres-cli",
    version=VERSION,
    entry_points='''
        [console_scripts]
        dnres=src.dnres_cli:dnres
    ''',
    author="Dimitrios Kioroglou",
    author_email="<d.kioroglou@hotmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['dnres', 'click', 'pandas'],
    include_package_data=True,
    keywords=['python', 'data analysis', 'bioinformatics', 'reporting', 'analysis results'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
