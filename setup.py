from setuptools import setup, find_packages

setup (
       name = "illuminate",
       version = "0.6.4",
       description = "Analytics toolkit for Illumina sequencer metrics.",
       url="https://bitbucket.org/invitae/illuminate",
       author = "Naomi Most",
       author_email = "naomi@nthmost.com",
       maintainer = "Naomi Most",
       maintainer_email = "naomi@nthmost.com",
       license = "MIT",
       zip_safe = False,
       packages = find_packages(),
       entry_points = { 'console_scripts': [
           'illuminate = illuminate.__main__:collect_args',] }, 
       install_requires = ["bitstring>=3.1.0",
                           "docopt",
                           "numpy>=1.6.2",
                           "pandas>=0.14",
                           "openpyxl>=1.8.6",
                           "xmltodict",
                           ],
     )
