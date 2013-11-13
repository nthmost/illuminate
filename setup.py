from setuptools import setup, find_packages

setup(
    name = "illuminate",
    version = "0.5.3",
    description = "Analytics toolkit for Illumina sequencer metrics.",
    url="https://bitbucket.org/invitae/illuminate",
    author = "InVitae Inc.",
    author_email = "developers@invitae.com",
    maintainer = "Naomi Most",
    maintainer_email = "naomi.most@invitae.com",
    license = "MIT",
    zip_safe = False,
    packages = find_packages(),
    install_requires = ["bitstring>=3.1.0",
                        "docopt",
                        "numpy>=1.6.2",
                        "pandas>=0.11",
                        ],
    )
